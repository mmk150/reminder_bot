{
  description = "Like diff but for Postgres schemas";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        self =
          {
            packages.thoth = pkgs.python3Packages.callPackage ./nix/thoth.nix { };
            defaultPackage = self.packages.thoth;
            devShells.thoth = (pkgs.python3.withPackages (p: with p; [
              pandas
              requests
              self.packages.thoth
              # other python packages you want
            ])).env;
            devShell = self.devShells.thoth;
          };
      in
      self);
}
