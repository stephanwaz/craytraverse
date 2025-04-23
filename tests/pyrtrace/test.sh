rxtrace -ab 2 -ad 20000 -lw 1e-5 -aa 0 -as 0 -I+ -ov -h sky.oct < rays.txt | rcalc -e '$1=$2' > rxtrace_out.txt
rxtrace -ab 2 -ad 20000 -lw 1e-5 -aa 0 -as 0 -I+ -ov -h sky.oct < rays.txt | rcalc -e '$1=$2' > rxtrace_out.txt
# rays2.txt has normals flipped
rxtrace -ab 2 -ad 20000 -lw 1e-5 -aa 0 -as 0 -I+ -ov -h sky.oct < rays2.txt | rcalc -e '$1=$2' > rxtrace_out2.txt

rlam rtrace_out.txt rxtrace_out2.txt  rxtrace_out.txt | neaten

# first two columns agree!
# 0.2252634        0.2261569        0.2201497
# 0.71777          0.7184336        0.03100657
# 0.3288274        0.3283888        0.1076967
# 0.03149364       0.03174186       0.02985469
# 0.1856359        0.184718         0.02019353
# 0.03442757       0.03485668       0.02712058