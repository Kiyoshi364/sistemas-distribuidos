{
  description = "A flake to run Julia for 'Algebra Linear Aplicada'";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:

    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells = let
            inself = self.devShells.${system};
        in {
          default = inself.python;
        
          python = pkgs.mkShell rec {
            name = "python-shell";

            buildInputs = with pkgs; [
              python310
              mypy
            ];

            shellHook = ''
              export PS1="\n\[\033[1;32m\][${name}: \w]\n\$\[\033[0m\] "
              export PURE="$([[ $IN_NIX_SHELL = 'pure' ]] && echo 1 || echo 0)"
              echo "PURE=$PURE"
              echo -n '>> Welcome to ${name}! <<'
            '';
          };
      };
    });
}
