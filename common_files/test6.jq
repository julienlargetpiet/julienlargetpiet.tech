reduce (
  paths
  | select(.[-1] == "name")
) as $p
  (.;
   setpath($p; (getpath($p) | ascii_upcase))
  )
