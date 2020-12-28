#!/usr/bin/env python3

import sys

# log error, information, etc.
class Stats():
    def __init__(self):
        self.entity_map = {}
        self.entity_map["All"] = 0
        return

    def add_entity(self, module_entity=None):
        if module_entity == None:
            module_entity = "All"
        if self.entity_map.__contains__(module_entity):
            self.entity_map[module_entity] += 1
        else:
            self.entity_map[module_entity] = 1

    def doState(self):
        print("-----======== Statics result ========-----")
        print("Total {} apk files".format(self.entity_map["All"]))
        c = 0
        for k in self.entity_map.keys():
            if k != "All":
                c += self.entity_map[k]
                print("Total {} apps match module {}, takes {}% of whole dataset".format(
                    self.entity_map[k],
                    k,
                    float(self.entity_map[k])/self.entity_map["All"] * 100)
                )

        print("Total {} apks match module signature, takes {}% of whole dataset".format(
            c,
            float(c)/self.entity_map["All"] * 100)
        )

        print("-----================-----")

def main():
    return

if __name__ == "__main__":
    sys.exit(main())
