class Transcript:
    def __init__(self, data, query: str = None):
        self.publicSets = None
        self.mustSets = None
        self.data = data
        self.query = query
        self.init()

    def init(self):
        sets = self.data["result"]["score"]["records"]
        self.mustSets = {}
        self.publicSets = {}
        for i in sets:
            if i['courseNature'] == '必修':
                self.mustSets[i['courseCname']] = (i['scoreText'], float(i['credit']))
            else:
                self.publicSets[i['courseCname']] = (i['scoreText'], float(i['credit']))

    def run(self):
        if self.query is not None:
            return self.mustSets[self.query] if self.query in self.mustSets.keys() else self.publicSets[self.query]
        else:
            self.mustSets.update(self.publicSets)
            return self.mustSets
