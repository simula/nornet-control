all:
	../Get-Nodes | awk '{ print $$2 }' | sort >nodes.list.tmp
	mv nodes.list.tmp nodes.list
