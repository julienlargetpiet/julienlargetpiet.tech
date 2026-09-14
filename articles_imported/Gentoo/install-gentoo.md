
In this article, we'll proceed to install Gentoo.

This article follows the story of manually installing Linux distros which begins here [https://julienlargetpiet.tech/articles/manually-installing-arch-and-void-linux-on-the-same-disk-with-uefi-and-grub.html](https://julienlargetpiet.tech/articles/manually-installing-arch-and-void-linux-on-the-same-disk-with-uefi-and-grub.html) where non Gentoo relative commands are explained in depth.

Indeed, we'll focus on Gentoo specific architecture here.

## Setup

We'll download the ISO here: [https://distfiles.gentoo.org/releases/amd64/autobuilds/current-install-amd64-minimal/](https://distfiles.gentoo.org/releases/amd64/autobuilds/current-install-amd64-minimal/).

Choose the adequat architecture, forme it's `amd64`.

Now, just copy the ISO onto an USB stick, or use Ventoy if you want.

For me I just do:

```bash

sudo dd if=/path/to/iso of=/dev/sdb conv=fsync bs=4M status=progress

```

Where `/dev/sdb` is of course my USB stick.

Now I just plug the USB stick onto my PC and boot onto it.

Hmm, you probably won't have this problem, but my screen cropped the tty and no way to fix this at this point, so I'll pipe the output of the next commands into `sed 's/^/      /'` to be able to properly see their output.

The `^` represents the start of each line, so I substituate it with 6 blank spaces.

Finally, I'm on the live Gentoo, let's begin the installation process !

## Partitioning

Now, I will just output the disks informations on this system:

```bash

lsblk -o NAME,SIZE,MODEL,FSTYPE,MOUNTPOINTS | sed 's/^/     /'

```

Output:

```

/dev/sda     465.8G   WDC WD5000AZLX-0  
└─/dev/sda1 465.8G   ext4

/dev/sdb      14.9G   USB Flash Drive   

```

My USB stick is obviously `/dev/sdb` and the target disk for the installation is `/dev/sda`.

The latter already contain a `/dev/sda1` partition formatted as an `ext4` filesystem, I'll wipe it out !

Also, I must detect if my PC supports UEFI.

Then, I just check `/sys/firmware/efi`:

```bash

ls /sys/firmware/efi

```

I see some files, then my PC accepts UEFI boot method.

We'll make 2 partitions, `/dev/sda1` for the ESP (about 500M) and one big `/dev/sda2` for the whole system.

Hmm, I prefere `parted` over `fdisk` so I'll do:

```bash

parted /dev/sda --script mklabel gpt \
  mkpart ESP FAT32 1MiB 513MiB \
  set 1 esp on \
  mkpart root ext4 513MiB 100%

```

Then, we'll format it:

```bash

mkfs.fat -F 32 -n ESP /dev/sda1
mkfs.ext4 -L root /dev/sda2

```

## Setting up `/mnt`

We'll mount the disk so we can access it from the live system:

```bash

mount /dev/sda2 /mnt/gentoo
mkdir -p /mnt/gentoo/boot/efi
mount /dev/sda1 /mnt/gentoo/boot/efi

```

For this step, I'll assume that we're connected through an Ethernet cable, so this ping must be successfull:

```bash

ping -c 3 julienlargetpiet.tech

```

If you just have the Wi-Fi antenna available, then detect its interface name with `ip link`, set it up with `ip link set dev INTERFACE-NAME up`, connect to the AP (Access Point) through `nmcli` if availaible (`nmcli device wifi connect "SSID-OR-BSSID" password "PASSWORD" ifname INTERFACE-NAME`) or through `wpa_supplicant` and `wpa_passpharse`.

Here's a much more detailed article about Wi-Fi on Linux:

[https://julienlargetpiet.tech/articles/i-just-wanted-wi-fi-to-work-on-linux.html](https://julienlargetpiet.tech/articles/i-just-wanted-wi-fi-to-work-on-linux.html)

Now that we checked that we had internet, we `cd /mnt/gentoo` and download a file containing the name of the latest tar file to download on the Gentoo server containing the required files for Gentoo:

```bash

/mnt/gentoo > wget https://distfiles.gentoo.org/releases/amd64/autobuilds/current-stage3-amd64-openrc/latest-stage3-amd64-openrc.txt

/mnt/gentoo > cat latest-stage3-amd64-openrc.txt

```

(And yess we'll use OpenRC instead of systemd)

Output:

```

Hash: SHA256

# Latest as of ...
...

stage3-amd64-openrc-20260811T083102Z.tar.xz

--- BEGIN PGP SIGNATURE ---

...

--- END PGP SIGNATURE ---


```

So now we download this tar file:

```bash

/mnt/gentoo > wget https://distfiles.gentoo.org/releases/amd64/autobuilds/current-stage3-amd64-openrc/stage3-amd64-openrc-20260811T083102Z.tar.xz

```

A `.tar` file is a file containing files and directories, the additional `.xz` extension means that this file is compresses using `xz`.

We use `xz` as it follow:

```bash

xz file.txt

```

turns:

```

file.txt

```

into:

```

file.txt.xz

```

and removes the original `file.txt` by default.

We can keep the original file while compressing with:

```bash

xz -k file.txt

```

To decompress it:

```bash

xz -d file.txt.xz

```

or equivalently:

```

unxz file.txt.xz

```

We can also add the `-k` flag to keep the `.xz` file.

Also, decompress to standard output instead of writing `teste.txt` with the `-c` flag:

```bash

xz -dc file.txt.xz

```

which is useful for things like:

```bash

xz -dc archive.tar.xz | tar -x

```

Which decompress the compressed `.xz` file (keeps it) and we pass the `stdout` to `tar -x` which then will extract the previously compressed archive.

But `tar` also supports direct decompression of `.xz` file with the `-J` flag.

Well, back to the installation.

Before extracting the Stage 3 archive, we should verify its integrity.

Gentoo provides a SHA256 checksum file alongside the Stage 3 archive, so we download it:

```bash

wget https://distfiles.gentoo.org/releases/amd64/autobuilds/current-stage3-amd64-openrc/stage3-amd64-openrc-20260811T083102Z.tar.xz.sha256

```

Then we ask `sha256sum` to verify the downloaded archive against that checksum:

```bash

sha256sum -c stage3-amd64-openrc-20260811T083102Z.tar.xz.sha256

```

If the archive is intact, we should get:

```

stage3-amd64-openrc-20260811T083102Z.tar.xz: OK

```

`-c` means check.

A `.sha256` file usually contains both:

```

<expected SHA256 hash>  <filename>

```

For example:

```

8f3a...c91d  stage3-amd64-openrc-20260811T083102Z.tar.xz

```

So when we ran the last command, `sha256sum` does this:

```

read expected hash from .sha256 file
        |
        V
read the filename from that same file
        |
        V
compute SHA256 of that local file
        |
        V
compare computed hash with expected hash

```

But we still need to verify that the downloaded archive really comes from Gentoo, because an attacker able to replace the tarball could theoretically also replace its SHA256 file.

That's kind of what OpenBSD advise to do, I speak about that in this article at the following section:

[https://julienlargetpiet.tech/articles/installing-openbsd-the-hard-way.html#installing-base-system](https://julienlargetpiet.tech/articles/installing-openbsd-the-hard-way.html#installing-base-system)

Gentoo also provides a detached OpenPGP signature alongside the Stage 3 archive:

```bash

wget https://distfiles.gentoo.org/releases/amd64/autobuilds/current-stage3-amd64-openrc/stage3-amd64-openrc-20260811T083102Z.tar.xz.asc

```

The `.asc` file is not the public key. It is the cryptographic signature of the Stage 3 archive, created using Gentoo's private signing key.

We must separately obtain/import Gentoo's trusted release public key and verify its fingerprint through a trusted Gentoo source.

`sec-keys/openpgp-keys-gentoo-release` is the Gentoo package name that contains the Gentoo release public keys.

When we boot the official Gentoo live ISO, that package is already installed in the live environment, so the key file is already present at something like:

```

/usr/share/openpgp-keys/gentoo-release.asc

```

So we can import it into the `gpg` environment:

```bash

gpg --import /usr/share/openpgp-keys/gentoo-release.asc

```

Once that public key is present in our GPG keyring, we can verify the archive:

```bash

gpg --verify stage3-amd64-openrc-20260811T083102Z.tar.xz.asc \
             stage3-amd64-openrc-20260811T083102Z.tar.xz

```

If the signature is valid and the signing key is trusted as Gentoo's real release key, we have authenticated the Stage 3 archive.

If you were not using the official Gentoo live ISO, Gentoo also documents fetching its key bundle directly:

```bash

wget -O - https://qa-reports.gentoo.org/output/service-keys.gpg | gpg --import

```

`-O` means write output to the following filename.

The following “filename” is:

```

-

```

and by convention `-` means standard output.

Then you can verify the signature in the same way

So the complete trust chain is:

```

trusted Gentoo public key
        |
        V
gpg --import ...
        |
        V
public key stored in ~/.gnupg keyring

```

And:

```

Stage3.tar.xz + Stage3.tar.xz.asc
        |
        V
gpg --verify ...
        |
        V
GPG retrieves Gentoo public key from keyring
        |
        V
signature valid / invalid

```

Now that we verified the authenticity of the tarball, we run:

```bash

/mnt/gentoo > tar xJpvf stage3-amd64-openrc-20260811T083102Z.tar.xz \
  --xattrs-include='*.*' \
  --numeric-owner

```

`-p` is for preserving file and folders permissions.

In addition to preserving this, we have `--xattrs-include="*.*"` meaning that `tar` should also preserve all metadata that matches this patter "*.*" (essentially all).

Indeed, maybe you didn't know about that but the inode corresponding to the file can have several key-value pairs, where the key is in fact composed of a namespace ant its attribute (such as `user.comment`), for example we use `setfattr` to set the attribute(s) of a file and `getfattr` to get its attribute(s).

```bash

setfattr -n user.comment -v "this is my comment" teste.txt.xz

setfattr -n user.comment2 -v "this is my comment 2" teste.txt.xz

```

And then to only get the key:

```bash

getfattr teste.txt.xz

```

Output:

```

# file: teste.txt.xz
user.comment
user.comment2

```

So now we can just query the particular value of a key:

```bash

getfattr -n user.comment2 teste.txt.xz

```

Output:

```

# file: teste.txt.xz
user.comment2="this is my comment 2"

```

Or we can directly query all (dump) with the `-d` flag:

```bash

getfattr -d teste.txt.xz

```

Output:

```

# file: teste.txt.xz
user.comment="this is my comment"
user.comment2="this is my comment 2"

```

Those commands also work for folders.

The available namespaces are:

- `user.*` -> general-purpose attributes for ordinary users and applications. On files we own, we can usually create arbitrary keys here, like `user.comment`.

And others namespaces that I'll describe in another article.

Now, `--numeric-owner` tells `tar` to resolve owner and group owner by respectively the UID and the GID instead of using the username and group name because those names often differs from the source environment to the destination environment (here `/mnt`).

A Gentoo Stage 3 tarball is the prebuilt minimal userspace filesystem tree that gives you a bootstrappable Gentoo system. It contains the standard directory hierarchy, core libraries, shell and basic utilities, Portage, package database metadata, configuration skeletons, ownerships, permissions, symlinks, and other filesystem metadata needed for the chosen architecture (here `amd64`).

We verify the hierarchy:

```bash

/mnt/gentoo > ls -la *

```

We should see something like:

```

bin
boot
dev
etc
home
lib
lib64
mnt
opt
proc
root
run
sbin
sys
tmp
usr
var

```

## First `chroot`

Here I've just `cd ../..`.

Now, we still have to mount some folders because at this point we're using the live kernel that directly communicates with those special folders.

Those folders contains special files, no creatable by decompressing tar because hardware-dependant (devices etcetera).

So because we also have to run commands on `/mnt/gentoo` to finalyze our system, and that those commands needs a complete envirnment to run.

Then, we'll sort of "make a proxy" of this environment into `/mnt/gentoo`.

But first, we can already copy the DNS configuration file from the live system to the target system:

```bash

cp --dereference /etc/resolv.conf /mnt/gentoo/etc/.

```

Here, we use `--dereference` flag because this can be a symlink and we don't want to copy the symlink itself, but the content it points to.

For example, here on my Debian12 machine, `/etc/resolv.conf` is a symlink:

```bash

ls -l /etc/resolv.conf

```

Output:

```

ls -l /etc/resolv.conf
lrwxrwxrwx 1 root root 39 déc.  18  2025 /etc/resolv.conf -> ../run/systemd/resolve/stub-resolv.conf

```

Setting the configuration directly at `/etc/resolv.conf` instead of a symlink to elsewhere is totally normal because programms that will search for DNS configuration are not able to see the difference from an actual normal file rather than a symlink at their layer.

Finally, we can proxy the live system to `/mnt/gentoo`:

```bash

mount --types proc /proc /mnt/gentoo/proc

mount --rbind /sys /mnt/gentoo/sys
mount --make-rslave /mnt/gentoo/sys

mount --rbind /dev /mnt/gentoo/dev
mount --make-rslave /mnt/gentoo/dev

mount --bind /run /mnt/gentoo/run
mount --make-slave /mnt/gentoo/run

```

The `--types proc` (or `-t proc`) explicitely describes the filesystem to mount.

Indeed, even if `mount` could have infered it, I prefere to be explicit because there is also `sysfs`, `devtmpfs`...

On my Debian 12 I got:

```bash

findmnt /dev

```

Output:

```

TARGET
     SOURCE
          FSTYPE   OPTIONS
/dev udev devtmpfs rw,nosuid,relatime,size=7117792k,nr_inodes=1779448,mode=755,inode64

```

And also for example:

```bash

findmnt /sys

```

Output:

```

TARGET
     SOURCE
           FSTYPE OPTIONS
/sys sysfs sysfs  rw,nosuid,nodev,noexec,relatime

```

But why no `--make-rslave` on it ?

Because for `/proc` we don't need to do that if we ask the kernel to make a new instance of `/proc` at another location (here `/mnt/gentoo/proc`).

Its' conceptually like:

```

kernel
  |-- provides procfs
  |
  |-- mounted at /proc
  |
  |-- mounted again at /mnt/gentoo/proc

```

We could theorically also make the same thing for the other special filesystem, here's an example for `/sys`:

```bash

mount -t sysfs /sys /mnt/gentoo/sys

```

But `/sys` can contain nested mounts created by other kernel subsystems or services

If you did only the above command, we would get a fresh top-level `sysfs`, but we would not automatically reproduce every separate mount living underneath the live system's `/sys`.

Now, the environment is correctly set, so we enter it:

```bash

chroot /mnt/gentoo /bin/bash

```

And we do:

```bash

source /etc/profile

```

`chroot` changes the filesystem root, but it does not rebuild the shell environment (inherits the live system’s environment). Therefore, after entering the Gentoo targeted install mount point, we source `/etc/profile` so the current shell loads Gentoo's environment variables and shell configuration instead of relying only on values inherited from the live system.

We can also make the difference visually clear between the 2 bash processes by modifying the current PS1:

```bash

export PS1="(chroot) ${PS1}"

```

It just prepend "(chroot)" to the current PS1.

## First contacts with `emerge`


The package manager of Gentoo is called **Portage** and its CLI is `emerge`.

For example we have:

```bash

emerge --sync

```

To update the packages database (versions, etcetera) (see later).

```bash

emerge pkg

```

To simply install a package (in this case `pkg`).

"install" here means that Portage resolves, fetches, builds if necessary, and merges/installs the package. `emerge --fetchonly pkg` is the download-only operation.

```bash

emerge --ask pkg

```

Resolves what would need to be done to install `pkg`, show us the planned package operations, then ask for confirmation before actually doing them.

Without `--ask`, Portage proceeds with the resolved operation without that confirmation prompt.

A very common Gentoo form is:

```bash

emerge --ask --verbose pkg

```

or:

```

emerge -av pkg

```

A typical output of that command would be:

```

These are the packages that would be merged, in order:

Calculating dependencies... done!
Dependency resolution took 1.17 s.


[ebuild  N     ] dev-libs/libfoo-1.4.2  USE="ssl -debug" 0 KiB
[ebuild  N     ] dev-libs/libbar-2.1.0  USE="threads" 0 KiB
[ebuild  N     ] app-misc/myprogram-3.7.1  USE="ssl threads -gtk" 850 KiB

Total: 3 packages (3 new), Size of downloads: 850 KiB

Would you like to merge these packages? [Yes/No]

```

"merge" means "install", "unmerge" means "uninstall" in the Portage terminology.

A typical general update command is:

```bash

emerge --update --deep --newuse @world

```

We can shorten it into:

```bash

emerge -uDN @world

```

This introduces the concept of packages set.

Semantically, that's packages group.

In Gentoo, we have the following:

- `@system` -> essential packages required by the active Gentoo profile.

- `@selected` -> packages you explicitly asked Portage to install.

- `@world` -> the overall managed system: roughly `@system` plus `@selected`.

- `@preserved-rebuild` -> packages that should be rebuilt because preserved libraries are still in use.

- `@module-rebuild` -> packages that build kernel modules and may need rebuilding after a kernel change.

`--update` tells Portage to prefer newer eligible versions of packages in the targeted set. It does not necessarily traverse their complete dependency trees. `emerge --sync`, by contrast, synchronizes the local Gentoo repository itself.

That's why we use the `--deep` flag, it tells Portage to also consider dependencies recursively.

And `--newuse` tells to Portage to rebuild packages that have seen their USE-flag change over their last build.

So even if a package has not received any update, if its USE-flag(s) have changed since its last build, then it'll be rebuilt.

To change the USE flag of a package we edit `/etc/portage/package.use/pkg` where `pkg` is the targeted package.

We can do that for example:

```bash

echo 'www-client/firefox wayland' >> /etc/portage/package.use/firefox

```

Back to the installation.

We need to download the Gentoo package repository metadata and `ebuilds` needed by Portage to install and manage software.

For that we run:

```bash

(chroot) > emerge-webrsync

```

The base system applications themselves mostly came from the Stage 3 tarball. `emerge-webrsync` just gives Portage the repository information it needs for future package operations.

To be sure that the local repository contains the last packages version (typically contained under `/var/db/repos/gentoo`) we do:

```bash

(chroot) > emerge --sync

```

## Choosing the profile

A profile is a system-wide **policy/configuration baseline** for Gentoo. It substantially influences how Portage configures and resolves the system.

Indeed, it will change this symlink `/etc/portage/make.profile` to point to the one selected, for example `/var/db/repos/gentoo/profiles/selected-profile`.

That profile defines the following:

- default USE flags

- forced USE flags

- masked USE flags

- package masks (blocked packages)

- default package choices

- the `@system` package set

- architecture defaults

- init-system defaults (here it'll be OpenRC)

- desktop-related defaults

- compiler/toolchain-related policy


To see all the available profiles, run:

```bash

(chroot) > eselect profile list

```

Personaly, I've chosen `[3] default/linux/amd64/23.0/desktop (stable)`.

So I did:

```bash

(chroot) > eselect profile set 3

```

We can verify the selected profile with:

```bash

(chroot) > eselect profile show

```

Expected output:

```

default/linux/amd64/23.0/desktop

```

## Locals an timezone

This is the general Linux step for the timezone:

```bash

(chroot) > ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime

```

Because I'm based in Paris, "Bonjour j'aime la baguette".

Alternatively, we could have set up the timezone, for me I would have run:

```bash

(chroot) > echo "Europe/Paris" > /etc/timezone

```

And then, we rerun the configuration script of the package `sys-libs`:

```bash

(chroot) > emerge --config sys-libs/timezone-data

```

It would have set the symlink correctly.

Then, set up your locals:

```bash

(chroot) > printf '%s\n' \
'en_US.UTF-8 UTF-8' \
'fr_FR.UTF-8 UTF-8' \
> /etc/locale.gen

```

Then we run:

```bash

(chroot) > locale-gen

```

It will compile the locale definitions to `/usr/lib/locale` for applications to use though the linux API.

Now, we'll choose the default locale for the system:

```bash

(chroot) > eselect locale list

```

As you guess, I've chosen `fr_FR.utf8`.

So I run:

```bash

(chroot) > eselect locale set 5

```

(`5` is the related numero for my locale)

I now reload the environment:

```bash

(chroot) > env-update
(chroot) > source /etc/profile
(chroot) > export PS1="(chroot) ${PS1}"

```

Now we can verify simply with `locale` to see our default locale, for me:

```

LANG=fr_FR.utf8

```

## Installing the kernel

I installed the precompiled kernel.

"Heresy, heresy ! On Gentoo we don't install binaries !!!" I may hear, but don't worry we'll cover the manually compiled path later on.

So, I ran:

```bash

(chroot) > emerge --ask sys-kernel/gentoo-kernel-bin

```

And that's all.

Or maybe this will fail because `sys-kernel/gentoo-kernel-bin` needs a dependency built with a special USE flag.

With:

```bash

(chroot) > emerge --ask --autounmask-write pkg

```

Portage may propose:

```

The following USE changes are necessary:
# required by pkg
>=dev-libs/bar-1.2 foo

```

and then write that change into under:

```

/etc/portage/package.use/

```

- `--autounmask` -> calculate and show configuration changes that would solve the dependency problem

- `--autounmask-write` -> also write those proposed changes into `/etc/portage`

This command has not yet installed the kernel onto the system because its configuration file are still not accepted.

They are written as candidates (`CONFIG_PROTECT`), for example:

```

/etc/portage/package.use/._cfg0000_somefile

```

Then:

```bash

(chroot) > dispatch-conf

```

or:

```bash

(chroot) > etc-update

```

lets us actually merge or use that proposed USE-flag change into the real configuration.

Here we can simply select `use-new` to replace our old config files by the one proposed.

It's safe only when we're sure replacing the existing config is intended. But that's a good practice to inspect the `diff` before choosing.

Then we (re)run:

```bash

(chroot) > emerge --ask sys-kernel/gentoo-kernel-bin

```

and Portage resolves again using the now-active configuration.

Now, the kernel `vmlinuz` and the `initramfs` must be present inside `/boot`.

With:

```bash

ls -l /boot

```

We can see:

```

config-<version>-gentoo-dist-bin
initramfs-<version>-gentoo-dist-bin.img
System.map-<version>-gentoo-dist-bin
vmlinuz-<version>-gentoo-dist-bin

```

So the flow is:

```

emerge --ask --autounmask-write pkg
        |
        V
Portage proposes/writes config changes
        |
        V
CONFIG_PROTECT may create ._cfg* files
        |
        V
dispatch-conf or etc-update
        |
        V
review/merge/replace by the changes
        |
        V
rerun emerge --ask pkg

```

Now, the manual way, here it is.

First, we download the latest selected version of Gentoo’s patched Linux kernel.

```bash

(chroot) > emerge --ask sys-kernel/gentoo-sources

```

It'll download it under `/usr/src/linux-<version>-gentoo/`.

At this point, there's only one kernel version (the one we've just download) present in the system, so:

```bash

(chroot) > eselect kernel list

```

Should propose only one choice.

You start seeing multiple choices later if you keep older kernel sources installed.

So select it:

```bash

(chroot) > eselect kernel set 1

```

Now:

```bash

cd /usr/src/linux

```

Because `/usr/src/linux` is a symlink to the selected versioned source tree.

The advantage of `/usr/src/linux` is that it always points to the kernel source tree currently selected by `eselect kernel`.

Now that we are in the kernel directory, we can configure it with `menuconfig`:

```bash

(chroot) /usr/src/linux > make menuconfig

```

This opens the kernel configuration interface where you choose things such as:

```

CPU features
filesystems
NVMe/SATA drivers
USB
network drivers
Wi-Fi
graphics
sound
device drivers
kernel features

```

The resulting configuration is written to:

```bash

/usr/src/linux/.config

```

Then compile:

```bash

(chroot) /usr/src/linux > make -j"$(nproc)"

```

This compiles both the kernel and all features you selected as modules with all cores (`nproc` gives us that).

On x86_64, the actual compressed kernel image ends up around:

```

/usr/src/linux/arch/x86/boot/bzImage

```

Then, we install the kernel modules:

```bash

(chroot) /usr/src/linux > make modules_install

```

This puts them under:

```

/lib/modules/<kernel-version>/

```

This is more or less a bunch of `cp` commands.

Now that the modules are installed, we still have to install the kernel:

We can do that with:

```bash

(chroot) /usr/src/linux > make install

```

or do the equivalent manual installation.

The manual version is conceptually:

```bash

(chroot) /usr/src/linux > cp arch/x86/boot/bzImage /boot/vmlinuz-6.x.y-gentoo
(chroot) /usr/src/linux > cp System.map /boot/System.map-6.x.y-gentoo

```

`System.map` is a symbol table for the compiled kernel. It maps kernel symbol names to addresses.

Conceptually:

```

ffffffff81000000  _text
ffffffff81012340  some_kernel_function
ffffffff81234560  another_function

```

That is useful for debugging things like kernel crashes, stack traces, and address-to-symbol resolution.

So if a kernel diagnostic contains an address like:

```

ffffffff81012340

```

`System.map` allow to associate it with:

```

some_kernel_function

```

On the manual kernel installation, we can still need the `initramfs` depending on how the kernel is built  (`menuconfig` options).

The crucial difference in `menuconfig` is:

- `[*]` or `<*>` -> built directly into the kernel

- `<M>` -> kernel module

If our root filesystem is `ext4` and we configure:

```

<M> The Extended 4 (ext4) filesystem

```

then we have a problem: the `ext4.ko` module normally lives in:

```

/lib/modules/<kernel-version>/

```

which itself is on our root filesystem. But the kernel needs `ext4` support before it can mount that filesystem, we need a temporary filesystem able to loead the modules, that's `initramfs`.

So if we're not sure, we install it:

```bash

(chroot) > emerge --ask sys-kernel/dracut

```

And then we generate the `initramfs` for our specific kernel version (`--kver`):

```bash

(chroot) > dracut --kver <version>-gentoo

```

Wich will create:

which typically creates something like:

```

/boot/initramfs-6.x.y-gentoo.img

```

Then GRUB can load both:

```

vmlinuz-6.x.y-gentoo
initramfs-6.x.y-gentoo.img

```

## `/etc/fstab`

We'll take the UUID of the partition to identify them, which is more robust.

We can identify them on `/dev/sda` with:

```bash

(chroot) > blkid /dev/sda1 /dev/sda2

```

Which will output something like:

```

/dev/sda1: UUID="D582-D4F9" BLOCK_SIZE="512" TYPE="vfat" PARTLABEL="ESP" PARTUUID="174a0abe-1272-fa44-b63f-411ad529cc20"
/dev/sda2: UUID="070eb80c-2ffc-45a0-83ab-3ee9c37a7dc8" BLOCK_SIZE="4096" TYPE="ext4" PARTLABEL="root" PARTUUID="60e9a40e-a90f-974e-af3c-7235b7e5d05f"

```

We can respectively assign the UUID to some variables:

```bash

ESP_UUID=$(blkid -o value -s UUID /dev/sda1)
ROOT_UUID=$(blkid -o value -s UUID /dev/sda2)

```

And then write this to `/etc/fstab`:

```bash

printf '%s\n' \
"UUID=$ROOT_UUID / ext4 defaults,noatime 0 1" \
"UUID=$ESP_UUID /boot/efi vfat defaults 0 2" \
> /etc/fstab

```

## Final configuration

We have first to set up the root password:

```bash

(chroot) > passwd

```

Now, setup the hostname, I'll call it "gentoo":

```bash

(chroot) > echo "gentoo" > /etc/hostname

```

Now, we install the tool that will ask the dhcp server our network configuration (IPV4 etcetera), and that's `dhcpcd`:

```bash

(chroot) > emerge --ask net-misc/dhcpcd

```

And we enable it for future boot (not with `systemd` because it's not present, but with `openrc`).

```bash

(chroot) > rc-update add dhcpcd default

```

The `default` is a runlevel, with `openrc` we have:

1. `sysinit` -> very early system initialization

2. `boot` -> services needed while booting

3. `default` -> normal everyday operating state

4. `shutdown` -> shutdown-related services

So `default` is roughly the normal multi-user state of the machine. It is where you normally enable services such as networking, SSH, cron, display managers, etc.

You can see which services belong to which runlevels with:

```bash

rc-update show

```

And specifically:

```bash

rc-update show default

```

To remove it again:

```bash

rc-update del dhcpcd default

```

The other major OpenRC command is `rc-service`. `rc-update` controls when a service should run automatically, while `rc-service` controls the service right now.

For example:

```bash

rc-service dhcpcd start
rc-service dhcpcd stop
rc-service dhcpcd restart
rc-service dhcpcd status

```

Here's a table showing the commands for `openrc` and `systemctl` for the same purpose:

| systemd | OpenRC |
|---|---|
| `systemctl start sshd` | `rc-service sshd start` |
| `systemctl stop sshd` | `rc-service sshd stop` |
| `systemctl restart sshd` | `rc-service sshd restart` |
| `systemctl status sshd` | `rc-service sshd status` |
| `systemctl enable sshd` | `rc-update add sshd default` |
| `systemctl disable sshd` | `rc-update del sshd default` |
| `systemctl enable --now sshd` | `rc-update add sshd default && rc-service sshd start` |
| `systemctl is-enabled sshd` | `rc-update show default \| grep sshd` |
| `systemctl list-units --type=service` | `rc-status` |

With OpenRC:

```bash

rc-update add dhcpcd default

```

registers the service in a `runlevel`. OpenRC then knows that when it enters `default`, `dhcpcd` should be running.

OpenRC does use runlevel directories containing symlinks to service scripts. Typically we see something like:

```

/etc/runlevels/
|-- sysinit/
|-- boot/
|-- default/
|-- nonetwork/
|-- shutdown/

```

So,

```

/etc/runlevels/default/sshd

```

is typically a symlink to:

```

/etc/init.d/sshd

```

And that init script then knows which executable to run, what dependencies it has, what arguments to pass, and how to stop it.

With `systemd`, a custom service does not need anything under `/etc/init.d/`. The unit file itself is the service definition (under `/etc/systemd/system/service-name`).

For example:

```

[Unit]
Description=My custom service

[Service]
ExecStart=/usr/local/bin/mydaemon

[Install]
WantedBy=multi-user.target

```

That is enough for `systemd` because the unit file tells it what binary to launch and how the service behaves.

With OpenRC, the equivalent service definition is usually an init script under:

```

/etc/init.d/mydaemon

```

For a simple daemon, it can be very small:

```bash

#!/sbin/openrc-run

command="/usr/local/bin/mydaemon"
command_background="yes"
pidfile="/run/mydaemon.pid"

```

Then make it executable:

```bash

chmod +x /etc/init.d/mydaemon

```

and enable it:

```bash

rc-update add mydaemon default

```

Nevertheless, a `systemd` unit’s `ExecStart=` can point to any executable command, including an `/etc/init.d/...` shell script.

But it is usually considered a compatibility approach rather than the preferred native systemd design.

## Grub

Now that we've done the minimum configurations, we do need to install bootloader and in this article it will be Grub:

```bash

(chroot) > emerge --ask sys-boot/grub

```

Ouch, I get a circular dependency error:

```

Error: circular dependencies:
...
dev-libs/glib
dev-python/docutils
dev-python/pillow
media-libs/harfbuzz
...

```

A circular dependency means that the current dependency graph has no valid build order. For example, building `A` requires `B`, while the selected configuration of `B` eventually requires `A` again.

Some dependency edges exist only when a particular USE flag is enabled. Portage noticed that disabling `Pillow`s `truetype` USE flag removes one of the edges forming the cycle:

```

A -> ... -> Pillow[truetype] -> ... -> A

```

becomes:

```

A -> ... -> Pillow

```

with the problematic dependency no longer required.

Portage can then find a valid build order. Once those packages are installed, we remove the temporary USE override and rebuild `Pillow` with its normal USE configuration.

That's why we have:

```

It might be possible to break this cycle
by applying the following change:

dev-python/pillow-12.3.0 (Change USE: -truetype)

```

So now we can create an arbitrary file nunder `/etc/portage/package.use/` containing this:

```

dev-python/pillow -truetype

```

Because when installing a package, Portage will read all the use flags written in all files in this directory.

So, we do:

```bash

(chroot) > echo "dev-python/pillow -truetype" > /etc/portage/package.use/grub-bootstrap

```

Because:

```

Pillow with truetype enabled
        |
        V
needs some additional library

```

but:

```

Pillow with truetype disabled
        |
        V
does not need that library

```

Indeed, in Gentoo USE syntax:

```

truetype

```

means enable the `truetype` USE flag, while:

```

-truetype

```

means disable it.

Then:

```bash

(chroot) > emerge --ask sys-boot/grub

```

Portage recalculates dependencies with:

```

Pillow:
truetype = OFF

```

and can hopefully build the dependency chain.

Just a little sidebar here.

Personaly, at this point I had to let the compilation all the night to finish, and at the morning I had the bad surprise to note that there wasn't even a video output from my PC.

So I had to completely shut it down, disconnect the power source, remove the RAM during several minutes and finally reboot it.

I booted on the live Gentoo ISO and mounted the `/dev/sda` partitions like we've done before.

I checked the Portage `emerge` last logs with:

```bash

(chroot) > tail -n 30 /var/log/emerge.log

```

And hopefully the package was successfully installed:

```

Completed emerge (186 of 186)
*** Finished. Cleaning up...
*** exiting successfully.
*** terminating.

```

Once the bootstrap is complete, that restriction is no longer necessarily required, because the packages involved in the circular dependency now already exist on the system. So we remove our temporary override:

```bash

(chroot) > rm /etc/portage/package.use/grub-bootstrap

```

Now the profile's normal settings apply again. If the profile wants:

```

truetype = ON

```

Portage sees that the installed Pillow was built with a different USE configuration. Therefore:

```bash

(chroot) > emerge --ask --newuse dev-python/pillow

```

Will rebuild `Pillow` according to its now-current USE configuration. Indeed, as written before `--newuse` flag tells Portage to recompile the targeted package if its last use flag(s) did not match with the current one(s).

You can verify that the installation of `sys-boot/grub` properly worked:

```bash

grub-install --version

```

Now, we finally can install `grub` in the ESP:

```bash

(chroot) > grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=Gentoo

```

Finally, we generate its configuration:

```bash

(chroot) > grub-mkconfig -o /boot/grub/grub.cfg

```

We can check if we see a "Gentoo" entry in the NVRAM with:

```bash

(chroot) > efibootmgr

```

And we must see this directory `/boot/efi/EFI/Gentoo` by recursively `ls` in `/boot/efi/EFI`:

```bash

ls -R /boot/efi/EFI

```

Or by the method you want (that was just to introduce you to the `-R` flag in `ls` lol).

## Exiting the target environment

Now, it's a good idea to tell the kernel to flush pending filesystems writes from memory to the storage device.


```bash

(chroot) > sync

```

And, we can finally exit:

```bash

(chroot) > exit

```

Finally, we recursively unmount all mount points under `/mnt/gentoo`:

```bash

umount -R /mnt/gentoo

```

And then we can finally reboot:

```bash

reboot

```

We'll make sure to unplug the USB sticks for the boot.

Congratulations, you finally have installed Gentoo !!!

## Conclusion

Hope this article was useful, see you later ;)









