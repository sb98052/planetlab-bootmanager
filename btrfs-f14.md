# Situation

On PLE we havea bunch of fedora14 BootCDs that seem to be able to perform installation of more recent fedoras on the hard drive, except for the version of btrfs-progs that ships on the BootCDs (0.
It would be nice to be more confident in the version of btrfs used for partitioning a disk when upgrading a node (in fact we need to reinstall because a vserver-based node only has ext2 filesystems)

# Proposal 
* Trying to install a binary from from more recent fedoras won't work as is because of the dependency to glibc6

* Idea is to rebuild a binary rpm that can be downloaded frmo the bootCD so that we use a more robust set of btrfs util tools.


# Build details

* Used a random f14 build VM (`2015-06-25--f14 x86_64`)

* started from the source rpm the fedora20 `btrfs-progs` (trying to take something not too recent either)

    http://fedora.mirrors.ovh.net/linux/updates/20/SRPMS/btrfs-progs-4.0-1.fc20.src.rpm

* manually installed missing deps

    yum -y install libuuid-devel libacl-devel libblkid-devel lzo-devel
    
* just ran this

#
    rpmbuild --rebuild http://fedora.mirrors.ovh.net/linux/updates/20/SRPMS/btrfs-progs-4.0-1.fc20.src.rpm
    cd /root/rpmbuild/RPMS/x86_64
    [root@2015-06-25--f14 x86_64]# ls -l
    total 5176
    -rw-r--r-- 1 root root  529920 Jun 25 14:49 btrfs-progs-4.0-1.fc14.x86_64.rpm
    -rw-r--r-- 1 root root 4718860 Jun 25 14:49 btrfs-progs-debuginfo-4.0-1.fc14.x86_64.rpm
    -rw-r--r-- 1 root root   42916 Jun 25 14:49 btrfs-progs-devel-4.0-1.fc14.x86_64.rpm
    
# showstopper

This rpm looks nice, it does not seem to have any odd dependency 
(although this needs more confirmation in the particular context of a f14 bootCD)

I have not been able to horseshoe it into the BootCD environment though 
because in this context **we have no extra space in the ramfs**, not even as small as 4Mb !!

Given that a f14 bootCD does seem fit to install a f22 hard drive, 
I will assume this is no big deal and proceed as-is;

For the record what I see right now in my builds is the f14 bootCD has

    # btrfs --version 
    Btrfs Btrfs v0.19

	
