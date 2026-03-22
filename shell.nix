{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    ruby
    gcc
    gnumake
    pkg-config
  ];
}
