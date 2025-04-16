{
  description = "Developer shell flake for Python development";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11"; 
  };

  outputs = { self, nixpkgs }: {
    devShells.x86_64-linux.default = let
        pkgs = nixpkgs.legacyPackages.x86_64-linux;
        python = pkgs.python314;
        # We currently take all libraries from systemd and nix as the default
        # https://github.com/NixOS/nixpkgs/blob/c339c066b893e5683830ba870b1ccd3bbea88ece/nixos/modules/programs/nix-ld.nix#L44
        pythonldlibpath = nixpkgs.lib.makeLibraryPath (with pkgs; [
          pkgs.taglib
          pkgs.git
          pkgs.libxslt
          pkgs.libzip
          pkgs.libz

          pkgs.zlib
          pkgs.zstd
          pkgs.stdenv.cc.cc
          pkgs.curl
          pkgs.openssl
          pkgs.attr
          pkgs.libssh
          pkgs.bzip2
          pkgs.libxml2
          pkgs.acl
          pkgs.libsodium
          pkgs.util-linux
          pkgs.xz
          pkgs.systemd
        ]);
        patchedpython = (python.overrideAttrs (
          previousAttrs: {
            # Add the nix-ld libraries to the LD_LIBRARY_PATH.
            # creating a new library path from all desired libraries
            postInstall = previousAttrs.postInstall + ''
              mv  "$out/bin/python3.14" "$out/bin/unpatched_python3.14"
              cat << EOF >> "$out/bin/python3.14"
              #!/run/current-system/sw/bin/bash
              export LD_LIBRARY_PATH="${pythonldlibpath}"
              exec "$out/bin/unpatched_python3.14" "\$@"
              EOF
              chmod +x "$out/bin/python3.14"
            '';
          }
        ));
      in
      pkgs.mkShell {
        name = "python-dev-shell";
        packages = with pkgs; [
          patchedpython
          mailcatcher
        ];

        shellHook = ''

          if test ! -d .venv; then
            python -m venv .venv
          else
            source ./.venv/bin/activate
          fi


          if test -f requirements.txt; then
            pip install -r requirements.txt
          fi

        '';
        venvDir = "./.venv";
        postVenvCreation = ''
          unset SOURCE_DATE_EPOCH
          pip install -r requirements.txt
        '';

        postShellHook = ''
          # allow pip to install wheels
          unset SOURCE_DATE_EPOCH
        '';
      };
  };
}

