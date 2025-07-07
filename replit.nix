{ pkgs }: {
  deps = [
    pkgs.psmisc
    pkgs.python-launcher
    pkgs.python312
    pkgs.python312Packages.pip
    pkgs.libstdcxx5
    pkgs.gcc-unwrapped.lib
    pkgs.stdenv.cc.cc.lib
    pkgs.git
  ];
}