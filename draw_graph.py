#!/usr/bin/python
WRAPPER = "digraph G { %s }"

def connect(n1, n2):
  return str(n1) + "->" + str(n2)

