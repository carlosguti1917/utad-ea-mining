import re

txt = "['/carts/{id}/deliveryaddresses', '/carts/{id}/itens/{itemid}', '/carts/{id}/paymentmethod', '/carts/{id}/itens', '/orders/{id}', '/carts/{id}', '/orders', '/carts', '/cep']"
txt1 = "/carts/{id}/deliveryaddresses"
txt2 = '/carts/{id}/itens/{itemid}'
txt3 = '/carts/{id}/itens'
txt4= '/orders/{id}'
txt5 = '/carts/{id}'
txt6 = '/carts'

x = re.search(r"(\b{0}\b/.*/\b{1}\b/.*)".format('carts', 'itens'), txt)
x1 = re.search(r"(/\bcarts\b/.*)", txt)
x2 = re.search(r"(\b{0}\b/.*)(\b{1}\b/.*)".format('carts', 'itens'), txt)
x3 = re.search(r"((?=.*/\bcarts\b/).*)|((?=.*\b/itens\b/).*).*$", txt)
x4 = re.fullmatch(r"(\b{0}\b/.*)".format('carts'), txt)

data = "/NOT (NOT A OR NOT B)/"
x5 = re.search("(?!(?!.*A)|(?!.*B))/.*$", data)
#Bingo
#v1 = ["carts", "itens"]
v1= "carts"
v2 = "itens"
x6 = re.search(r"(?!(?!.*{0}/)|(?!.*/{1}/.*))/.*$".format(v1, v2), txt1)
x7 = re.search(r"(?!(?!.*{0}/)|(?!.*/{1}/.*)).*$".format(v1, v2), txt1)
#'(?!(?!.*/carts//)|(?!.*/{/itens}/.*))/.*$'

print('x1=', x1)
print('x2=', x2)
print('x3=', x3)
print('x4=', x4)
print('x5=', x5.string)
if x6 is not None:
    print('x6=', x6.string)
if x7 is not None:
    print('x7=', x7.string)
print('xx=', "(?!(?!.*carts/)|(?!.*/itens/.*))/.*$")
print('xx=', '(?!(?!.*carts/)|(?!.*//itens/.*))/.*$')
            #'(?!(?!.*carts/)|(?!.*/{itens}/.*))/.*$'
