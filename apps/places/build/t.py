$i =1;
while (my $line= <STDIN>) { 
  chomp($line); 
  $line =~ s/\(/\($i,/g;
  $i++;
  print $line. "\n"; 
}
