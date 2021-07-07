from Crypto.Cipher import AES
from base64 import b64decode, b64encode
import hvac
import os
import json
import time

VAULT_ADDR = None
VAULT_TOKEN = None
VAULT_TRANSIT_KEYNAME = None

if "VAULT_ADDR" in os.environ and "VAULT_TOKEN" in os.environ and "VAULT_TRANSIT_KEYNAME":
    VAULT_ADDR = os.environ.get('VAULT_ADDR')
    VAULT_TOKEN = os.environ.get('VAULT_TOKEN')
    VAULT_TRANSIT_KEYNAME = os.environ.get('VAULT_TRANSIT_KEYNAME')
else:
    exit()

client = hvac.Client(
    url=VAULT_ADDR,
    token=VAULT_TOKEN,
    verify=True,
)

if not client.is_authenticated():
    print("Vault authentication failure.")
    exit()

try:
    gen_key_response = client.secrets.transit.generate_data_key(
        name=VAULT_TRANSIT_KEYNAME,
        key_type='plaintext',
    )
except NameError:
    exit()

plaintext = gen_key_response['data']['plaintext']
ciphertext = gen_key_response['data']['ciphertext']

data = "I'm baby gochujang twee kitsch fashion axe umami, tofu unicorn street art marfa tbh vaporware prism ennui ramps letterpress. Glossier williamsburg fanny pack, kale chips woke wolf coloring book mixtape cornhole keytar hell of pinterest fingerstache. IPhone lumbersexual authentic, street art photo booth narwhal butcher whatever roof party schlitz typewriter. Scenester viral authentic dreamcatcher selfies hot chicken deep v semiotics hoodie bitters yr. Drinking vinegar tumblr vape, wayfarers VHS celiac paleo tote bag. Knausgaard food truck vice prism.\nBanjo cliche meh salvia, schlitz ramps chambray tofu iPhone pour-over disrupt yr. Tattooed sustainable street art umami heirloom. Iceland pour-over gochujang, bushwick pork belly fixie tofu. Coloring book pork belly offal marfa shabby chic mumblecore raclette twee man braid affogato gluten-free selvage occupy flannel. Polaroid aesthetic keytar, artisan chambray irony meditation VHS XOXO try-hard asymmetrical.\nCeliac small batch cred, cornhole selfies enamel pin selvage synth. Pour-over la croix cray lomo cloud bread letterpress sustainable. Kogi cray tbh brooklyn raw denim pour-over. Poutine organic flannel prism intelligentsia XOXO listicle 90's squid. Ugh PBR & B palo santo, stumptown sustainable narwhal normcore man braid street art deep v shabby chic master cleanse mumblecore austin. Leggings viral farm-to-table vexillologist keffiyeh offal, roof party bicycle rights.\nSustainable disrupt pop-up, bicycle rights iPhone gochujang edison bulb farm-to-table wolf. Yuccie man braid franzen blue bottle small batch vexillologist hexagon poutine vegan single-origin coffee fam. Yr forage cold-pressed typewriter brooklyn migas. Organic aesthetic butcher pok pok, kickstarter farm-to-table scenester. Farm-to-table mustache subway tile tattooed everyday carry. Portland kombucha keytar forage live-edge, waistcoat polaroid subway tile fanny pack shaman chia wayfarers 3 wolf moon sriracha.\nTilde pickled portland lyft tattooed franzen master cleanse knausgaard intelligentsia pabst meh jean shorts photo booth enamel pin brooklyn. Put a bird on it activated charcoal kale chips sartorial tilde air plant, organic taxidermy iceland polaroid migas readymade gochujang la croix. Cloud bread enamel pin prism drinking vinegar tattooed, literally taiyaki authentic woke raw denim seitan. Church-key slow-carb pok pok tattooed, locavore organic cold-pressed. Kale chips squid selvage normcore food truck thundercats vice. Post-ironic gastropub marfa fam lo-fi offal vice jean shorts. Poke hella banjo, fingerstache snackwave butcher green juice tote bag food truck chambray.\nDummy text? More like dummy thicc text, amirite?"

key = b64decode(str(plaintext).encode('utf-8'))

e_cipher = AES.new(key, AES.MODE_EAX)
e_data = e_cipher.encrypt(b64encode(str(data).encode('utf-8')))

record_data = {}
record_data['nonce'] = str(b64encode(e_cipher.nonce).decode())
record_data['ciphertext'] = str(ciphertext)
record_data['data'] = str(b64encode(e_data).decode())

timestr = time.strftime("%Y%m%d%H%M%S")
filename = "data" + timestr + ".json"

print(record_data)
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(record_data, f, ensure_ascii=False)
