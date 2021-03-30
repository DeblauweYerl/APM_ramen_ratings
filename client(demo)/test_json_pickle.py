import jsonpickle as jsonpickle

from labo05.demo_networking.clientserver8.data.Som import Som

s1 = Som (12,452)
frozen = jsonpickle.encode(s1)
print(frozen)

my_writer_obj = open("demo.txt", mode='w')
my_writer_obj.write(frozen)
my_writer_obj.close()