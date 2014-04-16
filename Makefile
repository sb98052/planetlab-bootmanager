#

########## sync
# 2 forms are supported
# (*) if your plc root context has direct ssh access:
# make sync PLC=private.one-lab.org
# (*) otherwise, for test deployments, use on your testmaster
# $ run export
# and cut'n paste the export lines before you run make sync

PLCHOSTLXC ?= lxc64-1.pl.sophia.inria.fr

ifdef PLC
SSHURL:=root@$(PLC):/
SSHCOMMAND:=ssh root@$(PLC)
else
ifdef PLCHOSTLXC
SSHURL:=root@$(PLCHOSTLXC):/vservers/$(GUESTNAME)
SSHCOMMAND:=ssh root@$(PLCHOSTLXC) virsh -c lxc:/// lxc-enter-namespace $(GUESTNAME) -- /usr/bin/env 
else
ifdef PLCHOSTVS
SSHURL:=root@$(PLCHOSTVS):/vservers/$(GUESTNAME)
SSHCOMMAND:=ssh root@$(PLCHOSTVS) vserver $(GUESTNAME) exec
endif
endif
endif

LOCAL_RSYNC_EXCLUDES	:= --exclude '*.pyc' 
RSYNC_EXCLUDES		:= --exclude .svn --exclude .git --exclude '*~' --exclude TAGS $(LOCAL_RSYNC_EXCLUDES)
RSYNC_COND_DRY_RUN	:= $(if $(findstring n,$(MAKEFLAGS)),--dry-run,)
RSYNC			:= rsync -a -v $(RSYNC_COND_DRY_RUN) $(RSYNC_EXCLUDES)

DEPLOYMENT ?= regular

sync:
ifeq (,$(SSHURL))
	@echo "sync: I need more info from the command line, e.g."
	@echo "  make sync PLC=boot.planetlab.eu"
	@echo "  make sync PLCHOSTVS=.. GUESTNAME=.."
	@echo "  make sync PLCHOSTLXC=.. GUESTNAME=.. GUESTHOSTNAME=.."
	@exit 1
else
	$(SSHCOMMAND) mkdir -p /usr/share/bootmanager/$(DEPLOYMENT)
	+$(RSYNC) build.sh source $(SSHURL)/usr/share/bootmanager/$(DEPLOYMENT)
	$(SSHCOMMAND) /etc/plc.d/bootmanager start
endif

##########
tags:
	find . -type f | egrep -v 'TAGS|DIFF|/\.svn/|\.git/|~$$' | xargs etags

.PHONY: tags
