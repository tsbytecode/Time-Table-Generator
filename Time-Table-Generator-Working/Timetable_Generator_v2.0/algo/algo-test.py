# classes = [{'cls':'1A','periods': [['chem',3],['phy',3]]}]

# tasks = [{'cls':'1A','sub':'c','teacher':''}]

# teachers = [{name:'',t}]

#clss = [{'name':'1A','teachers':[{'name':'','subject':'','periods':0}]}]

import random

clss = [
  {
    "name": "1A",
    "teachers": [
      {"name": "m1", "subject": "Mathematics", "periods": 5},
      {"name": "sc1", "subject": "Science", "periods": 4},
      {"name": "e1", "subject": "English", "periods": 5},
      {"name": "h1", "subject": "Hindi", "periods": 4}
    ]
  },
  {
    "name": "1B",
    "teachers": [
      {"name": "sc1", "subject": "Science", "periods": 5},
      {"name": "m2", "subject": "Mathematics", "periods": 4},
      {"name": "e1", "subject": "English", "periods": 4},
      {"name": "ar1", "subject": "Art", "periods": 2},
      {"name": "cs1", "subject": "Computer Science", "periods": 3}
    ]
  },
  {
    "name": "1C",
    "teachers": [
      {"name": "m1", "subject": "Mathematics", "periods": 4},
      {"name": "sc2", "subject": "Science", "periods": 3},
      {"name": "e2", "subject": "English", "periods": 5},
      {"name": "ss1", "subject": "Social Studies", "periods": 4},
      {"name": "pe1", "subject": "Physical Education", "periods": 2}
    ]
  },
  {
    "name": "1D",
    "teachers": [
      {"name": "m2", "subject": "Mathematics", "periods": 5},
      {"name": "sc1", "subject": "Science", "periods": 4},
      {"name": "h1", "subject": "Hindi", "periods": 5},
      {"name": "ar1", "subject": "Art", "periods": 4}
    ]
  },
  {
    "name": "1E",
    "teachers": [
      {"name": "m1", "subject": "Mathematics", "periods": 3},
      {"name": "sc2", "subject": "Science", "periods": 5},
      {"name": "e2", "subject": "English", "periods": 4},
      {"name": "ss1", "subject": "Social Studies", "periods": 2},
      {"name": "cs1", "subject": "Computer Science", "periods": 4}
    ]
  }
]

teachers = {
  "m1": [],
  "sc1": [],
  "e1": [],
  "ss1": [],
  "h1": [],
  "m2": [],
  "ar1": [],
  "cs1": [],
  "sc2": [],
  "e2": [],
  "pe1": []
}


for cls1 in clss :
    tt = []
    # DONT USE CONSTANTS FOR SUCH THINGS
    for period in range(18) :
        posiblities = []

        for t in cls1['teachers'] :
            if 'nused' not in t.values() :
                t.setdefault('nused',t['periods'])
            if t['nused'] != 0 and period not in teachers[t['name']] :
                posiblities.append(t['name'])
        
        if len(posiblities) == 0 :
            print('unrecoverable shceduling conflict or SOMETHING IS BROKEN')
        else :
            name = posiblities[random.randint(0,len(posiblities)-1)]

            teachers[name].append(period)
            for y in cls1['teachers'] :
                if y['name'] == name :
                    y['nused'] -= 1
            
            tt.append(name)
    
    cls1.setdefault('tt',tt)
    print(cls1['name'],'\n\n',tt)