# Publishing

**You may not need this.** The file has no scripts, so there is nothing for Rive
to sign, and the unsigned build in `dist/pos_printing.riv` already plays in the
stock runtime (`tools/runtime-check` proves it). It also carries no watermark.

Use these steps if you want the file in your Rive account, an editable `.rev`
for a designer, or a build that went through `--publish`. All of them need you
to be signed in, which only works on your own machine.

## 1. Install the Rive CLI

macOS (Apple Silicon) or Linux (x86_64):

```bash
curl -fsSL https://releases.rive.app/cli/install.sh | sh
echo 'export PATH="$HOME/.rive/bin:$PATH"' >> ~/.zshrc   # or ~/.bashrc
source ~/.zshrc
rive --version
```

Windows (PowerShell): `irm https://releases.rive.app/cli/install.ps1 | iex`

## 2. Sign in

```bash
rive login     # opens a browser; you only do this once
rive whoami    # confirms who you are signed in as
```

Credentials stay on your machine (`~/.config/rive/app.rive.cli/` on macOS and
Linux, Credential Manager on Windows). Never paste them into a chat or commit
them.

## 3. Choose what you need

From the repo root:

```bash
cd pos_printing
```

**Put it in your Rive account (also removes any publish watermark):**

```bash
rive push .
```

This creates a Rive file and records its id in `pos_printing/rive.yaml` under
`push:`. Commit that change so later pushes update the same file.

**An editable copy for the Rive editor:**

```bash
rive . --once --rev=../dist/pos_printing.rev
```

**A published build:**

```bash
rive . --publish
cp build/pos_printing.riv ../dist/pos_printing.riv
```

`--publish` adds a watermark unless the project has been pushed (above) to a
workspace on the Cadet plan or higher.

## 4. Check it and commit

```bash
cd ../tools/runtime-check && npm install && node check.mjs
cd ../.. && git add dist pos_printing/rive.yaml && git commit -m "Publish pos_printing.riv"
```

Or send me the files and I'll commit them.
