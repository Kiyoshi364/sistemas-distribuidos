{
  description = "A flake to run Python for 'Sistemas Distribuidos'";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:

    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        myShell = input@{
            name,
            buildInputs ? [],
            toShellName ? n: "${n}-shell",
            shellHook ? { shellName, ... }: ''
              export PS1="\n\[\033[1;32m\][${shellName}: \W]\n\$\[\033[0m\] "
              export PURE="$([[ $IN_NIX_SHELL = 'pure' ]] && echo 1 || echo 0)"
              echo "PURE=$PURE"
              echo -n '>> Welcome to ${shellName}! <<'
            '',
          }: pkgs.mkShell {
            name = toShellName name;

            buildInputs = buildInputs;

            shellHook = shellHook
              (input // { shellName = toShellName name; });
          };
      in {
        devShells = let
            inself = self.devShells.${system};
        in {
          default = inself.python;
        
          python = myShell {
            name = "python";

            buildInputs = with pkgs; [
              less
              python310
              mypy
            ];
          };

          slides = myShell {
            name = "slides";
            buildInputs = with pkgs; [ slides ];
          };
      };
    });
}
