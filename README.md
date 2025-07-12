<p align="center">
    <a>Automatarr</a>
    <br/>
    <sup><em>Movie, TV, and Music Archival Software</em></sup>
</p>

## What is Automatarr?

Automatarr is a fork of [Devine](https://github.com/devine-dl/devine/), a powerful archival tool for downloading movies, TV shows, and music from streaming services. Built with a focus on modularity and extensibility, it provides a robust framework for content acquisition with support for DRM-protected content.

## Key Features

- 🚀 **Easy Installation** - Simple pip installation
- 🎥 **Multi-Media Support** - Movies, TV episodes, and music
- 🛠️ **Built-in Parsers** - DASH and HLS manifest support
- 🔒 **DRM Support** - Widevine and PlayReady integration
- 💾 **Flexible Storage** - Local and remote key vaults
- 👥 **Multi-Profile Auth** - Support for cookies and credentials
- 🤖 **Smart Naming** - Automatic P2P-style filename structure
- 🎬 **TMDB Lookup** - Automatic or Manual lookup for TMDB for muxing
- ⚙️ **Configurable** - YAML-based configuration
- ❤️ **Open Source** - Fully open-source with community contributions welcome

## Quick Start

### Installation

```shell
pip install automatarr
```

> [!NOTE]
> After installation, you may need to add the installation path to your PATH environment variable if prompted.

### Basic Usage

```shell
# Check available commands
automatarr --help

# Configure your settings
automatarr cfg --help

# Confirm setup and all dependencies exist
automaterr env check

# Download content (requires configured services)
automatarr dl SERVICE_NAME CONTENT_ID
```

## Documentation

For comprehensive setup guides, configuration options, and advanced usage:

📖 **[Visit our WIKI](https://github.com/automatarr/automatarr/wiki)**

The WIKI contains detailed information on:

- Installation and dependencies
- Service configuration
- Authentication setup
- DRM configuration
- Advanced features and troubleshooting

> [!WARNING]
> Only create or use services for platforms you have the legal right to access.

For guidance on creating services, see our [WIKI documentation](https://github.com/automatarr/automatarr/wiki).

## License

This software is licensed under the [GNU General Public License, Version 3.0](LICENSE).

**⚖️ Legal Notice**: Use Automatarr responsibly and only with content you have the legal right to access and download.

## Services

Automatarr doesn't include any services by default. You must create your own services for the platforms you have legal access to.

Unlike similar project's such as [youtube-dl], automatarr does not currently come with any Services. You must develop your
own Services and only use automatarr with Services you have the legal right to do so.

> [!NOTE]
> If you made a Service for automatarr that does not use widevine or any other DRM systems, feel free to make a Pull Request
> and make your service available to others. Any Service on [youtube-dl] (or [yt-dlp]) would be able to be added to the
> automatarr repository as they both use the [Unlicense license] therefore direct reading and porting of their code would be
> legal.

  [youtube-dl]: <https://github.com/ytdl-org/youtube-dl>
  [yt-dlp]: <https://github.com/yt-dlp/yt-dlp>
  [Unlicense license]: <https://choosealicense.com/licenses/unlicense>

### Service Tags

Service tags generally follow these rules:

- Tag can be between 2-4 characters long, consisting of just `[A-Z0-9i]{2,4}`.
  - Lower-case `i` is only used for select services. Specifically BBC iPlayer and iTunes.
- If the Service's commercial name has a `+` or `Plus`, the last character should be a `P`.
  E.g., `ATVP` for `Apple TV+`, `DSCP` for `Discovery+`, `DSNP` for `Disney+`, and `PMTP` for `Paramount+`.

These rules are not exhaustive and should only be used as a guide. You don't strictly have to follow these rules, but we recommend doing so for consistency.

### Sharing Services

Sending and receiving zipped Service folders is quite cumbersome. Let's explore alternative routes to collaborating on
Service Code.

> [!WARNING]
> Please be careful with who you trust and what you run. The users you collaborate with on Service
> code could update it with malicious code that you would run via automatarr on the next call.

#### Forking

If you are collaborating with a team on multiple services then forking the project is the best way to go.

1. Create a new Private GitHub Repository without README, .gitignore, or LICENSE files.
   Note: Do NOT use the GitHub Fork button, or you will not be able to make the repository private.
2. `git clone <your repo url here>` and then `cd` into it.
3. `git remote add upstream https://github.com/automatarr/automatarr`
4. `git remote set-url --push upstream DISABLE`
5. `git fetch upstream`
6. `git pull upstream master`
7. (optionally) Hard reset to the latest stable version by tag. E.g., `git reset --hard v1.0.0`.

Now commit your Services or other changes to your forked repository.  
Once committed all your other team members can easily pull changes as well as push new changes.

When a new update comes out you can easily rebase your fork to that commit to update.

1. `git fetch upstream`
2. `git rebase upstream/master`

However, please make sure you look at changes between each version before rebasing and resolve any breaking changes and
deprecations when rebasing to a new version.

If you are new to `git` then take a look at [GitHub Desktop](https://desktop.github.com).

> [!TIP]
> A huge benefit with this method is that you can also sync dependencies by your own Services as well!
> Just use `poetry` to add or modify dependencies appropriately and commit the changed `poetry.lock`.
> However, if the core project also has dependency changes your `poetry.lock` changes will conflict and you
> will need to learn how to do conflict resolution/rebasing. It is worth it though!

#### Symlinking

This is a great option for those who wish to do something like the forking method, but may not care what changes
happened or when and just want changes synced across a team.

This also opens up the ways you can host or collaborate on Service code. As long as you can receive a directory that
updates with just the services within it, then you're good to go. Options could include an FTP server, Shared Google
Drive, a non-fork repository with just services, and more.

1. Use any Cloud Source that gives you a pseudo-directory to access the Service files like a normal drive. E.g., rclone,
   Google Drive Desktop (aka File Stream), Air Drive, CloudPool, etc.
2. Create a `services` directory somewhere in it and have all your services within it.
3. [Symlink](https://en.wikipedia.org/wiki/Symbolic_link) the `services` directory to the `/automatarr` folder. You should
   end up with `/automatarr/services` folder containing services, not `/automatarr/services/services`.

You have to make sure the original folder keeps receiving and downloading/streaming those changes. You must also make
sure that the version of automatarr you have locally is supported by the Service code.

> [!NOTE]
> If you're using a cloud source that downloads the file once it gets opened, you don't have to worry as those will
> automatically download. Python importing the files triggers the download to begin. However, it may cause a delay on
> startup.

## Cookies & Credentials

automatarr can authenticate with Services using Cookies and/or Credentials. Credentials are stored in the config, and
Cookies are stored in the data directory which can be found by running `automatarr env info`.

To add a Credential to a Service, take a look at the [Credentials Config](CONFIG.md#credentials-dictstr-strlistdict)
for information on setting up one or more credentials per-service. You can add one or more Credential per-service and
use `-p/--profile` to choose which Credential to use.

To add a Cookie to a Service, use a Cookie file extension to make a `cookies.txt` file and move it into the Cookies
directory. You must rename the `cookies.txt` file to that of the Service tag (case-sensitive), e.g., `NF.txt`. You can
also place it in a Service Cookie folder, e.g., `/Cookies/NF/default.txt` or `/Cookies/NF/.txt`.

You can add multiple Cookies to the `/Cookies/NF/` folder with their own unique name and then use `-p/--profile` to
choose which one to use. E.g., `/Cookies/NF/sam.txt` and then use it with `--profile sam`. If you make a Service Cookie
folder without a `.txt` or `default.txt`, but with another file, then no Cookies will be loaded unless you use
`-p/--profile` like shown. This allows you to opt in to authentication at whim.

> [!TIP]
>
> - If your Service does not require Authentication, then do not define any Credential or Cookie for that Service.
> - You can use both Cookies and Credentials at the same time, so long as your Service takes and uses both.
> - If you are using profiles, then make sure you use the same name on the Credential name and Cookie file name when
>   using `-p/--profile`.
> [!WARNING]
> Profile names are case-sensitive and unique per-service. They have no arbitrary character or length limit, but for
> convenience sake we don't recommend using any special characters as your terminal may get confused.

### Cookie file format and Extensions

Cookies must be in the standard Netscape cookies file format.  
Recommended Cookie exporter extensions:

- Firefox: "[Export Cookies]" by `Rotem Dan`
- Chromium: "[Open Cookies.txt]" by `Ninh Pham`

  [Export Cookies]: <https://addons.mozilla.org/addon/export-cookies-txt>
  [Open Cookies.txt]: <https://chrome.google.com/webstore/detail/gdocmgbfkjnnpapoeobnolbbkoibbcif>

Any other extension that exports to the standard Netscape format should theoretically work.

## widevine Provisions

A widevine Provision is needed for acquiring licenses containing decryption keys for DRM-protected content.
They are not needed if you will be using automatarr on DRM-free services. Please do not ask for any widevine Device Files,
Keys, or Provisions as they cannot be provided.

automatarr only supports `.WVD` files (widevine Device Files). However, if you have the Provision RSA Private Key and
Device Client Identification Blob as blob files (e.g., `device_private_key` and `device_client_id_blob`), then you can
convert them to a `.WVD` file by running `pywidevine create-device --help`.

Once you have `.WVD` files, place them in the WVDs directory which can be found by calling `automatarr env info`.
You can then set in your config which WVD (by filename only) to use by default with `automatarr cfg cdm.default wvd_name`.
From here you can then set which WVD to use for each specific service. It's best to use the lowest security-level
provision where possible.

An alternative would be using a pywidevine Serve-compliant CDM API. Of course, you would need to know someone who is
serving one, and they would need to give you access. Take a look at the [remote_cdm](CONFIG.md#remotecdm-listdict)
config option for setup information. For further information on it see the pywidevine repository.

## End User License Agreement

automatarr and it's community pages should be treated with the same kindness as other projects.
Please refrain from spam or asking for questions that infringe upon a Service's End User License Agreement.

1. Do not use automatarr for any purposes of which you do not have the rights to do so.
2. Do not share or request infringing content; this includes widevine Provision Keys, Content Encryption Keys,
   or Service API Calls or Code.
3. The Core codebase is meant to stay Free and Open-Source while the Service code should be kept private.
4. Do not sell any part of this project, neither alone nor as part of a bundle.
   If you paid for this software or received it as part of a bundle following payment, you should demand your money
   back immediately.
5. Be kind to one another and do not single anyone out.

## Licensing

This software is licensed under the terms of [GNU General Public License, Version 3.0](LICENSE).  
You can find a copy of the license in the LICENSE file in the root folder.

* * *
