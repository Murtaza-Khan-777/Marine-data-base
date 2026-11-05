from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    raw_data = [
        {
            "name": "great white",
            "desc": "The great white shark is a species of large mackerel shark which can be found in the coastal surface waters of all the major oceans.",
            "habitat": "ocean",
            "img": "https://upload.wikimedia.org/wikipedia/commons/5/56/White_shark.jpg",
            "bgimg": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=2000&auto=format&fit=crop",
            "gradient": "from-blue-400 via-gray-300 to-white",
            "shadow": "rgba(96,165,250,0.4)",
            "glowclass": "glow-shark",
            "overlaygradient": "from-blue-900 via-slate-900 to-[#050510]"
        },
        {
            "name": "jellyfish",
            "desc": "Jellyfish and sea jellies are the informal common names given to the medusa-phase of certain gelatinous members of the subphylum Medusozoa.",
            "habitat": "ocean",
            "img": "https://upload.wikimedia.org/wikipedia/commons/4/44/Jelly_cc11.jpg",
            "bgimg": "https://images.unsplash.com/photo-1582967788606-a171c1080cb0?q=80&w=2000&auto=format&fit=crop",
            "gradient": "from-pink-400 via-purple-400 to-cyan-400",
            "shadow": "rgba(34,211,238,0.4)",
            "glowclass": "glow-jellyfish",
            "overlaygradient": "from-indigo-900 via-purple-900 to-[#050510]"
        },
        {
            "name": "sea turtle",
            "desc": "Sea turtles, sometimes called marine turtles, are reptiles of the order Testudines and of the suborder Cryptodira.",
            "habitat": "reef",
            "img": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Green_Sea_Turtle_grazing_seagrass.jpg",
            "bgimg": "https://images.unsplash.com/photo-1546026423-cc4642628d2b?q=80&w=2000&auto=format&fit=crop",
            "gradient": "from-green-400 via-teal-400 to-cyan-400",
            "shadow": "rgba(52,211,153,0.4)",
            "glowclass": "glow-turtle",
            "overlaygradient": "from-teal-900 via-cyan-900 to-[#050510]"
        }
    ]

    grouped_data = {}
    for item in raw_data:
        hab = item["habitat"]
        if hab not in grouped_data:
            grouped_data[hab] = []
        grouped_data[hab].append(item)

    for hab in grouped_data:
        grouped_data[hab] = sorted(grouped_data[hab], key=lambda x: x["name"])

    flat_data = []
    for hab in sorted(grouped_data.keys()):
        flat_data.extend(grouped_data[hab])

    return render_template('species.html', grouped_data=grouped_data, flat_data=flat_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)