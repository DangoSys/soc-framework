import os
import shutil
import subprocess
import time
from pathlib import Path

CDK = Path("/home/bb-runner/Code/eda/D_libraries/SMIC180/SRAM/S018SP_v0p1pc_CDK")
JAR = CDK / "S018SP.jar"

CORNERS = {
    "ss": "ss_1.62_125",
    "tt": "tt_1.8_25",
    "ff": "ff_1.98_125",
}


def resolve_corner(corner: str) -> str:
    if corner not in CORNERS:
        raise ValueError(f"smic180 corner must be one of {sorted(CORNERS)}, got {corner!r}")
    return CORNERS[corner]


def _pick_display() -> str:
    for n in range(99, 256):
        sock = Path(f"/tmp/.X11-unix/X{n}")
        lock = Path(f"/tmp/.X{n}-lock")
        if not sock.exists() and not lock.exists():
            return f":{n}"
    raise RuntimeError("no free X display in :99-255")


def _start_xvfb() -> tuple[subprocess.Popen, str]:
    path = os.pathsep.join(d for d in os.environ["PATH"].split(os.pathsep) if "verdi" not in d)
    xvfb = shutil.which("Xvfb", path=path)
    if xvfb is None:
        raise RuntimeError("Xvfb not on PATH (need nix develop / xorg-server)")
    display = _pick_display()
    n = display[1:]
    Path(f"/tmp/.X11-unix/X{n}").unlink(missing_ok=True)
    Path(f"/tmp/.X{n}-lock").unlink(missing_ok=True)
    proc = subprocess.Popen(
        [xvfb, display, "-screen", "0", "1024x768x24", "-ac"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    sock = Path(f"/tmp/.X11-unix/X{n}")
    for _ in range(50):
        if proc.poll() is not None:
            out = proc.stdout.read().decode() if proc.stdout else ""
            err = proc.stderr.read().decode() if proc.stderr else ""
            raise RuntimeError(f"Xvfb exited ({display}):\n{out}\n{err}")
        if sock.exists():
            return proc, display
        time.sleep(0.1)
    proc.terminate()
    out = proc.stdout.read().decode() if proc.stdout else ""
    err = proc.stderr.read().decode() if proc.stderr else ""
    raise RuntimeError(f"Xvfb socket timeout ({display}):\n{out}\n{err}")


def generate_smic180_sram_dbs(geoms, corner, cache_dir, lc_shell):
    java = os.environ.get("S018SP_JAVA")
    if not java:
        raise RuntimeError("S018SP_JAVA not set (need nix develop / jdk8)")
    if not Path(java).is_file():
        raise RuntimeError(f"missing S018SP_JAVA: {java}")
    tag = resolve_corner(corner)
    cache_dir = Path(cache_dir)
    dbs = []
    xvfb_proc = None
    env = None

    for g in sorted(geoms, key=lambda x: x.name):
        leaf = cache_dir / g.name
        v = leaf / f"{g.name}.v"
        lib = leaf / f"{g.name}_{tag}.lib"
        db = leaf / f"{g.name}_{tag}.db"

        if not v.is_file() or not lib.is_file():
            if xvfb_proc is None:
                cache_dir.mkdir(parents=True, exist_ok=True)
                xvfb_proc, display = _start_xvfb()
                env = os.environ.copy()
                env.pop("JAVA_TOOL_OPTIONS", None)
                env.pop("_JAVA_OPTIONS", None)
                env["MC_INSTALL_PATH"] = str(CDK)
                env["DISPLAY"] = display
                env["JAVA_HOME"] = str(Path(java).resolve().parent.parent)
            leaf.mkdir(parents=True, exist_ok=True)
            r = subprocess.run(
                [
                    java,
                    "-Djava.awt.headless=false",
                    "-jar",
                    str(JAR),
                    "-instname",
                    g.name,
                    "-words",
                    str(g.words),
                    "-mux",
                    str(g.mux),
                    "-bits",
                    str(g.bits),
                    "-v",
                    "-lib",
                    "-lef",
                    "-cdl",
                    "-savepath",
                    str(leaf),
                ],
                cwd=str(CDK),
                env=env,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                raise RuntimeError(f"S018SP failed ({g.name}):\n{r.stdout}\n{r.stderr}")
            if not v.is_file() or not lib.is_file():
                raise RuntimeError(
                    f"S018SP produced no v/lib ({g.name}): {v} {lib}\n{r.stdout}\n{r.stderr}"
                )

        if not db.is_file():
            if not lib.is_file():
                raise RuntimeError(f"missing liberty for lc_shell ({g.name}): {lib}")
            tcl = leaf / "lc.tcl"
            tcl.write_text(
                f"read_lib {{{lib}}}\n"
                f"write_lib [get_object_name [get_libs *]] -format db -output {{{db}}}\n"
                "exit\n"
            )
            r = subprocess.run(
                [str(lc_shell), "-f", str(tcl)],
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                raise RuntimeError(f"lc_shell failed ({g.name}):\n{r.stdout}\n{r.stderr}")
            if not db.is_file():
                raise RuntimeError(f"lc_shell produced no db ({g.name}): {db}")

        if not db.is_file():
            raise RuntimeError(f"sram db missing ({g.name}): {db}")
        dbs.append(db.resolve())

    if xvfb_proc is not None:
        xvfb_proc.terminate()
        xvfb_proc.wait()
    return dbs, tag
