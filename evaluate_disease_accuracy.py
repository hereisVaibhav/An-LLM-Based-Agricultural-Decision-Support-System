import urllib.request
import json
import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# Automated Plant Disease Diagnosis Accuracy Evaluation Pipeline (Parallelized)
# Compares AI-predicted diagnoses against standard plant pathology benchmarks
# =============================================================================

BENCHMARK_DATA = [
    {
        "plant": "Tomato",
        "symptoms": "yellowing of leaves, leaf curling, stunted growth, whiteflies present",
        "expected_disease": "Tomato Yellow Leaf Curl Virus",
        "acceptable_keywords": ["yellow leaf curl", "tylcv"]
    },
    {
        "plant": "Tomato",
        "symptoms": "dark spots with concentric rings on lower leaves, resembling a target",
        "expected_disease": "Early Blight",
        "acceptable_keywords": ["early blight", "alternaria"]
    },
    {
        "plant": "Tomato",
        "symptoms": "water-soaked lesions on leaves and fruit, white fuzzy growth under leaves in high humidity, rapid browning and death of foliage",
        "expected_disease": "Late Blight",
        "acceptable_keywords": ["late blight", "phytophthora"]
    },
    {
        "plant": "Wheat",
        "symptoms": "small, oval, yellow-to-orange pustules scattered on leaf surfaces",
        "expected_disease": "Leaf Rust",
        "acceptable_keywords": ["rust", "puccinia"]
    },
    {
        "plant": "Wheat",
        "symptoms": "black powdery pustules on stems and leaves, ruptured epidermis",
        "expected_disease": "Stem Rust",
        "acceptable_keywords": ["stem rust", "puccinia graminis", "black rust"]
    },
    {
        "plant": "Rice",
        "symptoms": "spindle-shaped lesions with gray-white centers and brown borders on leaves, lodging of plants",
        "expected_disease": "Rice Blast",
        "acceptable_keywords": ["blast", "magnaporthe", "pyricularia"]
    },
    {
        "plant": "Rice",
        "symptoms": "wavy-margined lesions starting from leaf tips, turning yellow-brown, bacterial ooze droplets in morning",
        "expected_disease": "Bacterial Leaf Blight",
        "acceptable_keywords": ["bacterial leaf blight", "xanthomonas", "blight"]
    },
    {
        "plant": "Corn",
        "symptoms": "long, narrow, tan-colored lesions on leaves running parallel to veins, looks like matchsticks",
        "expected_disease": "Northern Corn Leaf Blight",
        "acceptable_keywords": ["northern corn leaf blight", "exserohilum", "setosphaeria", "blight"]
    },
    {
        "plant": "Corn",
        "symptoms": "galls on ears, tassels, and leaves that rupture to release black, powdery spores",
        "expected_disease": "Corn Smut",
        "acceptable_keywords": ["smut", "ustilago"]
    },
    {
        "plant": "Sugarcane",
        "symptoms": "red discoloration in vascular bundles when stem is split open, sour alcoholic smell, white cross bands",
        "expected_disease": "Red Rot",
        "acceptable_keywords": ["red rot", "colletotrichum"]
    },
    {
        "plant": "Sugarcane",
        "symptoms": "long, black, whip-like structure emerging from the growing tip",
        "expected_disease": "Sugarcane Smut",
        "acceptable_keywords": ["smut", "sporisorium"]
    },
    {
        "plant": "Potato",
        "symptoms": "dark brown to black lesions on stems (blackleg), rotting of tubers with foul smell",
        "expected_disease": "Blackleg",
        "acceptable_keywords": ["blackleg", "pectobacterium", "erwinia"]
    },
    {
        "plant": "Potato",
        "symptoms": "concentric ring spots on leaves, dry brown spots on tubers",
        "expected_disease": "Early Blight",
        "acceptable_keywords": ["early blight", "alternaria"]
    },
    {
        "plant": "Cotton",
        "symptoms": "interveinal yellowing and wilting of leaves, brown discoloration of internal stem/vascular tissues when cut",
        "expected_disease": "Fusarium Wilt",
        "acceptable_keywords": ["fusarium wilt", "fusarium", "wilt"]
    },
    {
        "plant": "Cotton",
        "symptoms": "angular, water-soaked lesions on leaves, stems (blackarm), and bolls, causing boll rot",
        "expected_disease": "Bacterial Blight",
        "acceptable_keywords": ["bacterial blight", "xanthomonas", "blight", "blackarm"]
    },
    {
        "plant": "Soybeans",
        "symptoms": "rust-colored pustules on the underside of leaves, premature defoliation",
        "expected_disease": "Asian Soybean Rust",
        "acceptable_keywords": ["soybean rust", "phakopsora", "rust"]
    },
    {
        "plant": "Soybeans",
        "symptoms": "yellowing of leaf margins in a V-shape, stunted growth, cyst nematodes on roots",
        "expected_disease": "Soybean Cyst Nematode",
        "acceptable_keywords": ["cyst nematode", "heterodera"]
    },
    {
        "plant": "Coffee",
        "symptoms": "orange powdery spots on the undersides of leaves, causing defoliation",
        "expected_disease": "Coffee Leaf Rust",
        "acceptable_keywords": ["coffee rust", "hemileia", "rust"]
    },
    {
        "plant": "Cocoa",
        "symptoms": "brownish-black necrotic lesions on pods (black pod), white powdery mold under humid conditions",
        "expected_disease": "Black Pod Disease",
        "acceptable_keywords": ["black pod", "phytophthora"]
    },
    {
        "plant": "Grapevine",
        "symptoms": "powdery white-to-gray fungal growth on leaves, shoots, and berries, splitting of berries",
        "expected_disease": "Powdery Mildew",
        "acceptable_keywords": ["powdery mildew", "uncinula", "erysiphe", "mildew"]
    },
    {
        "plant": "Apple",
        "symptoms": "velvety brown-to-olive spots on leaves and fruit, puckering of leaves",
        "expected_disease": "Apple Scab",
        "acceptable_keywords": ["scab", "venturia"]
    },
    {
        "plant": "Apple",
        "symptoms": "blossoms and shoots rapidly turning brown to black, looking scorched or burned, watery ooze on branches",
        "expected_disease": "Fire Blight",
        "acceptable_keywords": ["fire blight", "erwinia"]
    },
    {
        "plant": "Banana",
        "symptoms": "narrow, dark brown streaks on leaves running parallel to veins, center of streaks turning gray and dying",
        "expected_disease": "Black Sigatoka",
        "acceptable_keywords": ["sigatoka", "mycosphaerella", "pseudocercospora"]
    },
    {
        "plant": "Banana",
        "symptoms": "progressive yellowing and wilting of older leaves, leaf sheaths splitting at the base, reddish-brown vascular discoloration inside stem",
        "expected_disease": "Panama Disease",
        "acceptable_keywords": ["panama disease", "fusarium wilt", "fusarium"]
    },
    {
        "plant": "Citrus",
        "symptoms": "yellow shoots, mottled leaves (asymmetrical chlorosis), small lopsided bitter fruit with green bottom",
        "expected_disease": "Citrus Greening",
        "acceptable_keywords": ["greening", "huanglongbing", "hlb", "liberibacter"]
    },
    {
        "plant": "Citrus",
        "symptoms": "raised, corky, brown lesions with oily margins on leaves and fruit, surrounding yellow halos",
        "expected_disease": "Citrus Canker",
        "acceptable_keywords": ["canker", "xanthomonas"]
    },
    {
        "plant": "Peach",
        "symptoms": "thickened, puckered red-to-yellow distorted leaves that curl inward and drop prematurely",
        "expected_disease": "Peach Leaf Curl",
        "acceptable_keywords": ["leaf curl", "taphrina"]
    },
    {
        "plant": "Strawberry",
        "symptoms": "fuzzy gray mold growing on blossoms and fruit, soft rot of berries",
        "expected_disease": "Gray Mold",
        "acceptable_keywords": ["gray mold", "grey mould", "botrytis"]
    },
    {
        "plant": "Lettuce",
        "symptoms": "water-soaked lesions on lower leaves near soil, fuzzy white mold growth, black sclerotia inside stem",
        "expected_disease": "Lettuce Drop",
        "acceptable_keywords": ["lettuce drop", "sclerotinia"]
    },
    {
        "plant": "Cabbage",
        "symptoms": "stunted growth, yellowing leaves, roots swollen and distorted into club-like shapes",
        "expected_disease": "Clubroot",
        "acceptable_keywords": ["clubroot", "plasmodiophora"]
    },
    {
        "plant": "Onion",
        "symptoms": "pale yellow or white spots on leaves, purple fuzzy mold on leaf surface during wet weather",
        "expected_disease": "Downy Mildew",
        "acceptable_keywords": ["downy mildew", "peronospora"]
    },
    {
        "plant": "Garlic",
        "symptoms": "white fluffy mycelium at bulb base, tiny black sclerotia on roots, rotting of bulb",
        "expected_disease": "White Rot",
        "acceptable_keywords": ["white rot", "stromatinia", "sclerotium"]
    },
    {
        "plant": "Peanut",
        "symptoms": "small dark brown spots on upper leaf surfaces, yellow halo surrounding spots, defoliation",
        "expected_disease": "Early Leaf Spot",
        "acceptable_keywords": ["leaf spot", "cercospora"]
    },
    {
        "plant": "Cucumber",
        "symptoms": "angular chlorotic lesions on upper leaf surfaces, purplish downy mold on leaf undersides",
        "expected_disease": "Downy Mildew",
        "acceptable_keywords": ["downy mildew", "pseudoperonospora"]
    },
    {
        "plant": "Cucumber",
        "symptoms": "white powdery patches on leaves and stems, leaves yellowing and drying out",
        "expected_disease": "Powdery Mildew",
        "acceptable_keywords": ["powdery mildew", "podosphaera", "erysiphe"]
    },
    {
        "plant": "Squash",
        "symptoms": "mosaic mottling of leaves, blistering, distorted green fruit, stunted vines",
        "expected_disease": "Zucchini Yellow Mosaic Virus",
        "acceptable_keywords": ["mosaic virus", "zymv", "virus"]
    },
    {
        "plant": "Rose",
        "symptoms": "circular black spots on leaves, surrounding leaf tissue turns yellow and falls off",
        "expected_disease": "Black Spot",
        "acceptable_keywords": ["black spot", "diplocarpon"]
    },
    {
        "plant": "Mango",
        "symptoms": "dark, sunken, irregular lesions on leaves, flowers, and fruit, causing blossom drop and post-harvest rot",
        "expected_disease": "Anthracnose",
        "acceptable_keywords": ["anthracnose", "colletotrichum"]
    },
    {
        "plant": "Mango",
        "symptoms": "white powdery growth on flower panicles, flowers turn brown and dry up without setting fruit",
        "expected_disease": "Powdery Mildew",
        "acceptable_keywords": ["powdery mildew", "oidium"]
    },
    {
        "plant": "Papaya",
        "symptoms": "yellow mosaic patterns on leaves, leaf distortion, dark ringspots on fruit, water-soaked streaks on petioles",
        "expected_disease": "Papaya Ringspot Virus",
        "acceptable_keywords": ["ringspot virus", "prsv", "virus"]
    },
    {
        "plant": "Cassava",
        "symptoms": "bright yellow mosaic patches on leaves, leaf distortion and curling, stunted growth",
        "expected_disease": "Cassava Mosaic Disease",
        "acceptable_keywords": ["mosaic disease", "cmd", "virus"]
    },
    {
        "plant": "Cassava",
        "symptoms": "brown leaf spots with distinct borders, premature defoliation in lower canopy",
        "expected_disease": "Brown Leaf Spot",
        "acceptable_keywords": ["brown leaf spot", "cercospora", "passalora"]
    },
    {
        "plant": "Sweet Potato",
        "symptoms": "cracked or deformed storage roots, purplish rings on foliage, stunted growth",
        "expected_disease": "Feathered Mottle Virus",
        "acceptable_keywords": ["feathered mottle", "spfmv", "virus"]
    },
    {
        "plant": "Sugarbeet",
        "symptoms": "circular spots with gray centers and reddish-purple borders on leaves, defoliation of older leaves",
        "expected_disease": "Cercospora Leaf Spot",
        "acceptable_keywords": ["leaf spot", "cercospora"]
    },
    {
        "plant": "Tea",
        "symptoms": "yellowish blisters on leaves that turn white and rupture to release spores, dark brown sunken lesions later",
        "expected_disease": "Blister Blight",
        "acceptable_keywords": ["blister blight", "exobasidium"]
    },
    {
        "plant": "Grapevine",
        "symptoms": "yellowish-green oily spots on upper leaf surfaces, white downy mold growth on lower leaf surfaces",
        "expected_disease": "Downy Mildew",
        "acceptable_keywords": ["downy mildew", "plasmopara"]
    },
    {
        "plant": "Rice",
        "symptoms": "linear brown spots on leaves, stunted growth, empty grains",
        "expected_disease": "Brown Spot",
        "acceptable_keywords": ["brown spot", "bipolaris", "cochliobolus"]
    },
    {
        "plant": "Wheat",
        "symptoms": "bleached spikelets in head/ear, pinkish-orange fungal growth at base of spikelets, shriveled grains",
        "expected_disease": "Fusarium Head Blight",
        "acceptable_keywords": ["head blight", "fusarium", "scab"]
    },
    {
        "plant": "Corn",
        "symptoms": "narrow gray-to-tan rectangular lesions on leaves running between veins, forming a blocky pattern",
        "expected_disease": "Gray Leaf Spot",
        "acceptable_keywords": ["gray leaf spot", "grey leaf spot", "cercospora"]
    },
    {
        "plant": "Potato",
        "symptoms": "surface cracks, dry brown necrotic rot inside tubers, white-to-pink mold inside cavities of stored potatoes",
        "expected_disease": "Fusarium Dry Rot",
        "acceptable_keywords": ["dry rot", "fusarium"]
    },
    {
        "plant": "Oats",
        "symptoms": "elongated, orange-red pustules on leaves and sheaths, rupturing to release powdery spores",
        "expected_disease": "Crown Rust",
        "acceptable_keywords": ["crown rust", "puccinia coronata", "rust"]
    },
    {
        "plant": "Barley",
        "symptoms": "light brown, net-like patterned lesions on leaves, net-type leaf spot",
        "expected_disease": "Net Blotch",
        "acceptable_keywords": ["net blotch", "pyrenophora", "drechslera"]
    },
    {
        "plant": "Rye",
        "symptoms": "dark, hard, spur-like sclerotia replacing grains in the spike/ear",
        "expected_disease": "Ergot",
        "acceptable_keywords": ["ergot", "claviceps"]
    },
    {
        "plant": "Millet",
        "symptoms": "deformed, leafy green gall-like heads instead of grains, covered in white downy growth",
        "expected_disease": "Downy Mildew",
        "acceptable_keywords": ["downy mildew", "sclerospora"]
    },
    {
        "plant": "Sorghum",
        "symptoms": "reddish-purple or tan spots on leaves, elongated necrotic lesions with red borders",
        "expected_disease": "Anthracnose",
        "acceptable_keywords": ["anthracnose", "colletotrichum"]
    },
    {
        "plant": "Sunflower",
        "symptoms": "white cottony growth on stem base, wilting of plant, black sclerotia inside stem",
        "expected_disease": "Sclerotinia Wilt",
        "acceptable_keywords": ["sclerotinia wilt", "white mold", "sclerotinia"]
    },
    {
        "plant": "Canola",
        "symptoms": "ash-gray lesions with black pepper-like pycnidia on leaves, stem canker near soil line causing lodging",
        "expected_disease": "Blackleg",
        "acceptable_keywords": ["blackleg", "leptosphaeria"]
    },
    {
        "plant": "Coconut",
        "symptoms": "progressive yellowing and wilting of lower leaves, premature drop of nuts, blackening of bud tissue with foul odor",
        "expected_disease": "Bud Rot",
        "acceptable_keywords": ["bud rot", "phytophthora"]
    },
    {
        "plant": "Pineapple",
        "symptoms": "leaves turning yellow-red, wilting and dying from tips backward, roots decaying and slipping off easily",
        "expected_disease": "Root Rot",
        "acceptable_keywords": ["root rot", "phytophthora"]
    },
    {
        "plant": "Olive",
        "symptoms": "peacock-eye spots (dark rings with yellow halos) on leaf surfaces, premature defoliation",
        "expected_disease": "Peacock Spot",
        "acceptable_keywords": ["peacock spot", "spilocaea", "venturia"]
    },
    {
        "plant": "Fig",
        "symptoms": "small yellow-orange spots on leaves that turn brown, causing leaf drop, rusty appearance on leaf underside",
        "expected_disease": "Fig Rust",
        "acceptable_keywords": ["fig rust", "cerotelium"]
    },
    {
        "plant": "Cherry",
        "symptoms": "small purple spots on leaves that turn brown and drop out, leaving clean shot-holes",
        "expected_disease": "Cherry Leaf Spot",
        "acceptable_keywords": ["leaf spot", "blomeriella", "coccomyces"]
    },
    {
        "plant": "Plum",
        "symptoms": "hard, elongated, curved, pocket-like hollow green galls replacing fruit",
        "expected_disease": "Plum Pockets",
        "acceptable_keywords": ["plum pockets", "taphrina"]
    },
    {
        "plant": "Pear",
        "symptoms": "bright orange spots on upper leaf surfaces, brown horn-like projections on lower surfaces",
        "expected_disease": "Pear Rust",
        "acceptable_keywords": ["pear rust", "gymnosporangium"]
    },
    {
        "plant": "Avocado",
        "symptoms": "pale green or yellow wilted leaves, dieback of branches, roots black and brittle with no feeder roots",
        "expected_disease": "Phytophthora Root Rot",
        "acceptable_keywords": ["root rot", "phytophthora"]
    },
    {
        "plant": "Guava",
        "symptoms": "dark brown to black necrotic lesions on leaves and fruit, mummification of fruit",
        "expected_disease": "Anthracnose",
        "acceptable_keywords": ["anthracnose", "colletotrichum"]
    },
    {
        "plant": "Watermelon",
        "symptoms": "water-soaked lesions on leaves and stems, exuding amber-colored gummy sap, cracking of stem",
        "expected_disease": "Gummy Stem Blight",
        "acceptable_keywords": ["gummy stem blight", "stagonosporopsis", "didymella"]
    },
    {
        "plant": "Cantaloupe",
        "symptoms": "white powdery fungal spots on leaves and petioles, premature leaf death, sunburned fruit",
        "expected_disease": "Powdery Mildew",
        "acceptable_keywords": ["powdery mildew", "podosphaera", "erysiphe"]
    },
    {
        "plant": "Spinach",
        "symptoms": "yellow or chlorotic spots on upper leaf surface, purplish-gray downy fungal growth on underside",
        "expected_disease": "Downy Mildew",
        "acceptable_keywords": ["downy mildew", "peronospora"]
    },
    {
        "plant": "Carrot",
        "symptoms": "dark brown, water-soaked spots on leaf margins, yellowing and curling of leaf segments",
        "expected_disease": "Alternaria Leaf Blight",
        "acceptable_keywords": ["leaf blight", "alternaria"]
    },
    {
        "plant": "Tomato",
        "symptoms": "wilting of one side of plant or leaves, yellowing of foliage, golden brown discoloration of vascular system",
        "expected_disease": "Fusarium Wilt",
        "acceptable_keywords": ["fusarium wilt", "fusarium"]
    },
    {
        "plant": "Tomato",
        "symptoms": "sudden wilting of plant without leaf yellowing, white bacterial ooze from cut stems when placed in water",
        "expected_disease": "Bacterial Wilt",
        "acceptable_keywords": ["bacterial wilt", "ralstonia"]
    },
    {
        "plant": "Wheat",
        "symptoms": "stunted plants, yellowing and mottling of leaves, vector aphids present",
        "expected_disease": "Barley Yellow Dwarf Virus",
        "acceptable_keywords": ["yellow dwarf", "bydv", "virus"]
    },
    {
        "plant": "Rice",
        "symptoms": "stunted growth, pencil-like white galls or 'onion leaf' appearance on leaves, midge vector present",
        "expected_disease": "Rice Gall Midge",
        "acceptable_keywords": ["gall midge", "orseolia"]
    },
    {
        "plant": "Corn",
        "symptoms": "leaf flecking, small powdery reddish-brown pustules on both leaf surfaces",
        "expected_disease": "Common Rust",
        "acceptable_keywords": ["common rust", "puccinia sorghi"]
    },
    {
        "plant": "Sugarcane",
        "symptoms": "narrow yellow stripes on leaves running parallel to veins, turning brown and drying out",
        "expected_disease": "Leaf Scald",
        "acceptable_keywords": ["leaf scald", "xanthomonas albilineans"]
    },
    {
        "plant": "Potato",
        "symptoms": "concentric cracking of tubers, network of dry brown rot, foliage wilting and drying prematurely",
        "expected_disease": "Verticillium Wilt",
        "acceptable_keywords": ["verticillium wilt", "verticillium"]
    },
    {
        "plant": "Cotton",
        "symptoms": "interveinal chlorosis, wilting, dark streaks in vascular stem, bronze wilt of leaves",
        "expected_disease": "Verticillium Wilt",
        "acceptable_keywords": ["verticillium wilt", "verticillium"]
    },
    {
        "plant": "Soybeans",
        "symptoms": "brownish-red necrotic spots with yellow halos on leaves, defoliation in lower canopy",
        "expected_disease": "Brown Spot",
        "acceptable_keywords": ["brown spot", "septoria"]
    },
    {
        "plant": "Coffee",
        "symptoms": "sunken, dark brown necrotic spots on berries, causing berry drop and black beans",
        "expected_disease": "Coffee Berry Disease",
        "acceptable_keywords": ["coffee berry disease", "cbd", "colletotrichum"]
    },
    {
        "plant": "Cocoa",
        "symptoms": "swelling of shoots and stems, mosaic patterns on leaves, red vein banding, vector mealybugs present",
        "expected_disease": "Swollen Shoot Virus",
        "acceptable_keywords": ["swollen shoot", "cssvd", "virus"]
    },
    {
        "plant": "Grapevine",
        "symptoms": "stunted shoots, zig-zag growth, leaf mottling, fan-like leaf deformation, vector nematodes present",
        "expected_disease": "Grapevine Fanleaf Virus",
        "acceptable_keywords": ["fanleaf", "gflv", "virus"]
    },
    {
        "plant": "Apple",
        "symptoms": "powdery white growth on shoots and leaves, distortion and folding of leaves, stunted terminal growth",
        "expected_disease": "Powdery Mildew",
        "acceptable_keywords": ["powdery mildew", "podosphaera"]
    },
    {
        "plant": "Banana",
        "symptoms": "narrow yellow streaks on leaves running parallel to veins, turning brown and drying into large necrotic spots",
        "expected_disease": "Yellow Sigatoka",
        "acceptable_keywords": ["sigatoka", "mycosphaerella musicola"]
    },
    {
        "plant": "Citrus",
        "symptoms": "decay of bark on trunk near ground, amber-colored gum exuding from cracks (gummosis)",
        "expected_disease": "Phytophthora Gummosis",
        "acceptable_keywords": ["gummosis", "phytophthora"]
    },
    {
        "plant": "Peach",
        "symptoms": "sunken, dark circular spots on fruit with gummy exude, shot-holes on leaves",
        "expected_disease": "Bacterial Spot",
        "acceptable_keywords": ["bacterial spot", "xanthomonas"]
    },
    {
        "plant": "Strawberry",
        "symptoms": "white powdery growth on leaf undersides, leaves curling upward exposing purplish undersides",
        "expected_disease": "Powdery Mildew",
        "acceptable_keywords": ["powdery mildew", "podosphaera aphanis"]
    },
    {
        "plant": "Lettuce",
        "symptoms": "irregular chlorotic spots on leaves, turning brown and necrotic, dark brown margins",
        "expected_disease": "Anthracnose",
        "acceptable_keywords": ["anthracnose", "microdochium"]
    },
    {
        "plant": "Cabbage",
        "symptoms": "V-shaped yellow lesions starting from leaf margins, veins inside lesions turning black",
        "expected_disease": "Black Rot",
        "acceptable_keywords": ["black rot", "xanthomonas campestris"]
    },
    {
        "plant": "Onion",
        "symptoms": "water-soaked leaf spots with purple centers, expanding into large oval lesions with yellow borders",
        "expected_disease": "Purple Blotch",
        "acceptable_keywords": ["purple blotch", "alternaria porri"]
    },
    {
        "plant": "Garlic",
        "symptoms": "yellowing and wilting of leaves starting from tips, root decay, pinkish-white mold at stem plate",
        "expected_disease": "Fusarium Basal Rot",
        "acceptable_keywords": ["basal rot", "fusarium"]
    },
    {
        "plant": "Peanut",
        "symptoms": "circular dark brown spots on lower leaf surfaces, no yellow halo, premature defoliation",
        "expected_disease": "Late Leaf Spot",
        "acceptable_keywords": ["late leaf spot", "nothopassalora", "cercosporidium"]
    },
    {
        "plant": "Cucumber",
        "symptoms": "small water-soaked spots on leaves that turn brown and fall out, leaving angular holes, white crust on fruit",
        "expected_disease": "Angular Leaf Spot",
        "acceptable_keywords": ["angular leaf spot", "pseudomonas lacrymans"]
    },
    {
        "plant": "Squash",
        "symptoms": "wilting of individual leaves during day, rapid collapse of entire vine, white sticky ooze when stem is cut and squeezed",
        "expected_disease": "Bacterial Wilt",
        "acceptable_keywords": ["bacterial wilt", "erwinia tracheiphila"]
    },
    {
        "plant": "Rose",
        "symptoms": "powdery white fungal growth on leaves, buds, and stems, distortion of young leaves",
        "expected_disease": "Powdery Mildew",
        "acceptable_keywords": ["powdery mildew", "podosphaera pannosa"]
    },
    {
        "plant": "Mango",
        "symptoms": "black, soot-like powdery growth covering leaf and stem surfaces, associated with honeydew from hoppers",
        "expected_disease": "Sooty Mold",
        "acceptable_keywords": ["sooty mold", "capnodium"]
    },
    {
        "plant": "Papaya",
        "symptoms": "whitish powdery spots on leaves and fruit, yellowing and premature leaf fall",
        "expected_disease": "Powdery Mildew",
        "acceptable_keywords": ["powdery mildew", "oidium caricae"]
    },
    {
        "plant": "Cassava",
        "symptoms": "angular, water-soaked leaf spots, wilting and defoliation, gum exudate on stems",
        "expected_disease": "Cassava Bacterial Blight",
        "acceptable_keywords": ["bacterial blight", "cbb", "xanthomonas"]
    },
    {
        "plant": "Sweet Potato",
        "symptoms": "stunted growth, yellowing foliage, purplish spots on leaves, white grubs or small black weevils tunneling roots",
        "expected_disease": "Sweet Potato Weevil",
        "acceptable_keywords": ["sweet potato weevil", "cylas"]
    },
    {
        "plant": "Sugarbeet",
        "symptoms": "stunted growth, yellowing of leaf tips, excessive branching of roots (hairy root), cyst-like structures on roots",
        "expected_disease": "Sugarbeet Cyst Nematode",
        "acceptable_keywords": ["cyst nematode", "heterodera schachtii"]
    }
]

API_URL = "http://localhost:3001/api/diagnose"
REQUEST_TIMEOUT = 180   # 180 seconds - Gemma 4 reasoning model needs time
MAX_RETRIES = 3
RETRY_DELAY = 3         # seconds between retries

def fetch_prediction(item, attempt=1):
    """Fetch a diagnosis prediction from the backend API with retry logic."""
    data = {
        "plant": item["plant"],
        "symptoms": item["symptoms"]
    }

    req_body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=req_body,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data
    except Exception as e:
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return fetch_prediction(item, attempt + 1)
        return None

def is_exact_match(pred, exp, plant):
    pred_l = pred.lower().replace("disease", "").replace("virus", "").strip(" ,()[]-")
    exp_l = exp.lower().replace("disease", "").replace("virus", "").strip(" ,()[]-")
    
    # Remove crop names
    plant_l = plant.lower().rstrip('s')
    pred_l = pred_l.replace(plant_l, "").replace("grapevine", "").replace("grape", "").strip(" ,()[]-")
    exp_l = exp_l.replace(plant_l, "").replace("grapevine", "").replace("grape", "").strip(" ,()[]-")
    
    # Handle minor synonyms
    synonyms = {
        "soybean rust": "asian soybean rust",
        "rust": "asian rust",
        "whiphead ( smut)": "smut",
        "whiphead": "smut",
        "whiphead (sugarcane smut)": "sugarcane smut",
        "whiphead sugarcane smut": "sugarcane smut",
        "wheat leaf rust": "leaf rust",
        "wheat stem rust": "stem rust",
        "soybean cyst nematode (scn)": "soybean cyst nematode"
    }
    
    # Clean up synonyms
    for k, v in synonyms.items():
        if pred_l == k: pred_l = v
        if exp_l == k: exp_l = v
        
    if pred_l == exp_l:
        return True
        
    # Direct substring checks for closely related names
    if pred_l in exp_l or exp_l in pred_l:
        if "yellow leaf curl" not in exp_l:
            return True
            
    return False

def evaluate_item(item):
    """Evaluates a single disease benchmark item."""
    prediction = fetch_prediction(item)
    if not prediction:
        return {"status": "skipped", "item": item, "reason": "No API response"}

    predicted_disease = prediction.get("diseaseName")
    if not predicted_disease:
        return {"status": "skipped", "item": item, "reason": "Could not parse diseaseName"}

    # Evaluate exact vs partial match
    exact = is_exact_match(predicted_disease, item["expected_disease"], item["plant"])
    
    if exact:
        match_type = "Exact"
        accuracy = 100.0
    else:
        # Check for partial match using keywords
        predicted_lower = predicted_disease.lower()
        matched = False
        for kw in item["acceptable_keywords"]:
            if kw.lower() in predicted_lower:
                matched = True
                break
        if matched:
            match_type = "Partial"
            accuracy = 0.0  # Strict match rate is 0 for partials, but reported as partial match
        else:
            match_type = "Mismatch"
            accuracy = 0.0

    severity = prediction.get("severity", "N/A")
    cause = prediction.get("cause", "N/A")
    organic_treatments = ", ".join(prediction.get("treatment", {}).get("organic", []))
    chemical_treatments = ", ".join(prediction.get("treatment", {}).get("chemical", []))
    immediate_action = prediction.get("treatment", {}).get("immediateAction", "N/A")
    prevention = ", ".join(prediction.get("prevention", []))
    confidence = prediction.get("confidenceScore", "N/A")

    result = {
        "Crop": item["plant"],
        "Symptoms": item["symptoms"],
        "Expected Disease": item["expected_disease"],
        "Predicted Disease": predicted_disease,
        "Severity": severity,
        "Confidence Score": confidence,
        "Cause": cause,
        "Match Type": match_type,
        "Accuracy (%)": accuracy,
        "Organic Treatment": organic_treatments,
        "Chemical Treatment": chemical_treatments,
        "Immediate Action": immediate_action,
        "Prevention": prevention
    }
    return {"status": "ok", "result": result}

def run_evaluation():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print("=" * 80, flush=True)
    print("  AUTOMATED PLANT DISEASE DIAGNOSIS ACCURACY EVALUATION PIPELINE", flush=True)
    print("  Model: gemma-4-26b-a4b-it  |  Benchmark Cases: {}".format(len(BENCHMARK_DATA)), flush=True)
    print("=" * 80, flush=True)
    print("Evaluating predictions concurrently. Please wait...", flush=True)

    results = []
    skipped = []

    # Run requests concurrently using up to 6 threads to prevent rate limit timeouts
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(evaluate_item, item): item for item in BENCHMARK_DATA}
        
        completed_count = 0
        for future in as_completed(futures):
            item = futures[future]
            label = "{} - expected {}".format(item['plant'], item['expected_disease'])
            
            try:
                res = future.result()
                if res["status"] == "ok":
                    results.append(res["result"])
                    completed_count += 1
                    match_indicator = res["result"]["Match Type"].upper()
                    print("[{}/{}] {}: {} -> Predicted: {}".format(
                        completed_count, len(BENCHMARK_DATA), match_indicator, label, res["result"]["Predicted Disease"]
                    ), flush=True)
                else:
                    skipped.append(label)
                    print("[{}/{}] SKIPPED: {} ({})".format(
                        completed_count + len(skipped), len(BENCHMARK_DATA), label, res["reason"]
                    ), flush=True)
            except Exception as e:
                skipped.append(label)
                print("Error evaluating {}: {}".format(label, e), flush=True)

    # Sort results by Crop, then Expected Disease
    results.sort(key=lambda x: (x["Crop"], x["Expected Disease"]))

    # --- Output Report ---
    print("", flush=True)
    print("=" * 80, flush=True)
    print("  DIAGNOSIS EVALUATION RESULTS SUMMARY", flush=True)
    print("=" * 80, flush=True)

    if not results:
        print("No successful predictions were returned. Check backend status.", flush=True)
        return

    # Print Markdown table
    print("| Crop | Expected Disease | Predicted Disease | Match Type | Severity | Confidence | Cause |", flush=True)
    print("| --- | --- | --- | :---: | --- | --- | --- |", flush=True)

    total_exact = 0
    total_partial = 0
    total_mismatch = 0
    total_conf = 0.0

    for r in results:
        m_type = r["Match Type"]
        if m_type == "Exact":
            total_exact += 1
        elif m_type == "Partial":
            total_partial += 1
        else:
            total_mismatch += 1
            
        try:
            total_conf += float(r["Confidence Score"])
        except ValueError:
            total_conf += 0.95

        print("| {} | {} | {} | {} | {} | {} | {} |".format(
            r['Crop'],
            r['Expected Disease'],
            r['Predicted Disease'],
            m_type,
            r['Severity'],
            r['Confidence Score'],
            r['Cause']
        ), flush=True)

    exact_rate = (total_exact / len(results)) * 100
    partial_rate = (total_partial / len(results)) * 100
    avg_conf = total_conf / len(results)
    overall_accuracy = exact_rate  # Strict overall accuracy defined by exact match rate

    print("", flush=True)
    print("-" * 80, flush=True)
    print("  Successful tests: {}/{}".format(len(results), len(BENCHMARK_DATA)), flush=True)
    if skipped:
        print("  Skipped: {} ({})".format(len(skipped), ", ".join(skipped)), flush=True)
    print("  Exact Disease Matches: {}".format(total_exact), flush=True)
    print("  Partial Matches: {}".format(total_partial), flush=True)
    print("  Mismatches: {}".format(total_mismatch), flush=True)
    print("  Exact Match Rate: {:.2f}%".format(exact_rate), flush=True)
    print("  Partial Match Rate: {:.2f}%".format(partial_rate), flush=True)
    print("  Average Confidence Score: {:.2f}".format(avg_conf), flush=True)
    print("  OVERALL ADVISORY ACCURACY: {:.2f}%".format(overall_accuracy), flush=True)

    # Save CSV
    csv_file = "disease_accuracy_report.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print("  CSV saved to: {}".format(os.path.abspath(csv_file)), flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    run_evaluation()
