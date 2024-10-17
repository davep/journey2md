# journey2md

## Introduction

This is a simple command line tool that can be used to extract journal
entries from [Journey](https://journey.cloud) and turn them into a
collection of Markdown files. In this tool's case the Markdown collection is
built so it can easily be used as an [Obsidian](https://obsidian.md) Vault.

## Installing

> [!NOTE]
> Ignore this section for the moment, this is a placeholder.

### pipx

The package can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install journey2md
```

### Homebrew

The package is available via Homebrew. Use the following commands to install:

```sh
$ brew tap davep/homebrew
$ brew install journey2md
```

## Usage

### Getting ready to use

The first thing you will need to do is create a full ZIP backup of your
Journey data, once you've done that unzip the backup file into a directory,
so that all the JSON data and photo attachments are individually available.

### Assumptions for the "Vault"

As mentioned earlier, this tool assumes that you're going to be making an
Obsidian Vault with the resulting Markdown. With this in mind the tool makes
the following assumptions:

- You wish to have a `YYYY/MM/DD` folder hierarchy for the entries.
- You prefer to have all attachments held in a `attachments` folder below
  the location of the entry the attachments are for.

These are my preferences, if yours differ it should be simple enough to
modify the code to taste (or, if what you prefer seems like it could be a
reasonable configuration option, create an issue in the repo and tell me all
about it).

### Create the target "Vault"

Create a directory where the "Vault" will be created. Note that `journey2md`
creates all directories and files *within* this directory.

### Perform the conversion

With all the above done and in mind, run the tool like this:

```sh
journey2md journey-data markdown-vault
```

where `journey-data` is the path to the directory that holds all of the
extracted Journey backup files, and where `markdown-vault` is the directory
you created that will be the Vault.

## Getting help

If you need help please feel free to [raise an
issue](https://github.com/davep/journey2md/issues).

[//]: # (README.md ends here)
