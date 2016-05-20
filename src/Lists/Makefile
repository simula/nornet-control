all:
	../Get-Nodes | awk '{ print $$2 }' | sort >nodes.list.tmp
	mv nodes.list.tmp nodes.list
	rm -f simula.list
	cat *.list | grep "\.simula\.nornet$$" | sed -s 's/\.simula\.nornet$$//g' | sort -u >simula.list
