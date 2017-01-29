def tarjan(V, E):
	'''
	Tarjan's strongly connected components algorithm
	https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm
	
	@param E
	@param V
	@return list of components
	'''
	class Node:
		def __init__(self, index, lowlink):
			self.index = index
			self.lowlink = lowlink
	
	def strongconnect(v, E, index, S, ctx):
		result = []
		#~ // Set the depth index for v to the smallest unused index
		ctx[v] = Node(index, index)
		index += 1
		S.append(v)
		
		print "S: ", S
		
		#~ // Consider successors of v
		for e in E:
			if e[0] == v:
				w = e[1]
				#~ if (w.index is undefined) then
				if w not in ctx:
					#~ // Successor w has not yet been visited; recurse on it
					result.extend( strongconnect(w, E, index, S, ctx) )
					ctx[v].index = min( ctx[v].lowlink, ctx[w].lowlink )
				elif w in S:
					#~ // Successor w is in stack S and hence in the current SCC
					ctx[v].index = min( ctx[v].lowlink, ctx[w].lowlink )

		#~ // If v is a root node, pop the stack and generate an SCC
		if ctx[v].lowlink == ctx[v].index:
			#~ start a new strongly connected component
			C = []
			#~ print "New S=", v, S
			while True:
				w = S.pop()
				C.append(w)
				if w == v:
					break
			#~ output the current strongly connected component
			#~ print "Component", C #, "S=", S
			
			result.append(C)
			
		return result

	index = 0
	S = []
	ctx = {}
	result = []
	for v in V:
		if v not in ctx:
			result.extend( strongconnect(v, E, index, S, ctx) )
			
	return result
