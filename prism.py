#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

from util2 import Arff2Skl


class Prism():

    def __init__(self, dataf):
        assert(os.path.exists(dataf))
        self._cvt = Arff2Skl(dataf)

    def fit(self, label=[]):
        data, attributes = (self._cvt.to_dict(),
                            self._cvt.meta.names())
        #print data
        if not label:
            label = attributes[-1]
        
        # classes stores all possible values for the class
        # ex: class 'contact-lenses' can be 'none', 'soft' or 'hard', so classes = ['none','soft','hard']
        classes = self._cvt.meta[label][1]
        
        # R is a list that stores all the rules
        R = []
        for cls in classes:
            #print cls # yes no
            # instances are the rows of the dataset
            instances = data[:]
            
            #print self.__has_class_value(instances, label, cls) # yes:9 no:5
            while self.__has_class_value(instances, label, cls):
                rule, covered = self.__build_rule(instances, attributes,
                                                  label, cls)
                R.append({cls: rule})
                instances = self.__remove_covered_instances(instances, covered)
        

        return R, label

    def __build_rule(self, instances, attributes, label, cls):
        R, accuracy = [], -1.0
        rule_instances = instances[:] # lines in dataset
        avail_attr = [a for a in attributes if a != label] # avail_attr is ['outlook','temperature','humidity','windy']

        #initialize the best_rule list to return
        best_rule = []

        # if available attributes not empty AND relevent rule accuracy less than 1.0(stops at 1.0)
        while avail_attr and accuracy < 1.0:
          #rule list to store best rule append by all other instances covered by a specific rule
          rule = []
          for a in avail_attr:
            #value list all values ('sunny','rainy','overcast') of an attribute ('outlook','temperature','humidity','')
            values = self.__get_attr_values(instances, a)
            for v in values:
              rule.append(best_rule + [(a,v)]) #each a and v is formatted as a tuple then append to rule
          #pass all rules in rule list to function get_best_rule
          best_rule = self.__get_best_rule(rule, rule_instances, label, cls)
          #smaller rule_instances list specified by the best rule
          rule_instances = self.__apply_rule(instances, best_rule)

          accuracy = self.__rule_accuracy(rule_instances, label, cls)[0]
          #smaller avail_attr list till it gets to empty
          avail_attr = self.__attr_not_in_R(avail_attr, best_rule)
          
          R = best_rule



        return R, rule_instances

    def __get_best_rule(self, rules, data, label, cls):
        best_rule = []
        bestrule_accuracy = (-1.0, -1)
        #accuracy_list = []
        for r in rules:
          coverage = self.__apply_rule(data, r)
          if(len(coverage)>0):
            #print coverage
            r_accuracy = self.__rule_accuracy(coverage, label, cls)
            
            if r_accuracy[0] > bestrule_accuracy[0]:
              best_rule = r
              bestrule_accuracy = r_accuracy
            #if accuracy the same then choose the bigger t
            elif r_accuracy[0] == bestrule_accuracy[0] and r_accuracy[1]>bestrule_accuracy[1]:
              best_rule = r
              bestrule_accuracy = r_accuracy
              

        #rule = sorted(rules, key = lambda x: x[1])
        

        return best_rule

    

    # This method returns the instances covered by the set of rules
    def __apply_rule(self, data, R):
        coverage = data[:]
        for r in R:
            coverage = [i for i in coverage if i[r[0]] == r[1]]
        return coverage

    # This method remove all instances covered by the set of rules
    def __remove_covered_instances(self, instances, covered):
        return [i for i in instances if i not in covered]

    # Computes p/t
    def __rule_accuracy(self, coverage, label, cls):
        accuracy = [i for i in coverage if i[label] == cls]
        return float(len(accuracy))/len(coverage), len(accuracy)

    # Counts how many instances of a given label have the specified class
    # ex: how many 'contact-lenses' = 'hard'
    def __has_class_value(self, instances, label, cls):
        #print label,cls
        asd = [i for i in instances if i[label] == cls]
        return len(asd)
    
    # Returns a list of all possible values of a given attribute
    def __get_attr_values(self, instances, attr):
        return self.__unique([a[attr] for a in instances])

    # Returns a list of all unique values of a list
    def __unique(self, l):
        return list(set(l))

    # Returns list of attributes not present in the rules
    def __attr_not_in_R(self, attr, R):
        return [a for a in attr if a not in [r[0] for r in R]]


# Debugging function printing the set of rules in english
def printRules(rules,label):
    for rule in rules:
        k = rule.keys()[0]
        nbr = len(rule[k])
        
        theRule = " IF "
        for subrules in rule[k]:
            nbr -= 1
            theRule = theRule + str(subrules[0]) + " = " + subrules[1]
            if nbr > 0:
                theRule = theRule + "\n\t AND "
            else:
                theRule = theRule + "\n\t THEN " + label + " = " + k
        
        print theRule +"\n"


if __name__ == '__main__':
    import sys
    prism = Prism(sys.argv[1])
    rules, label = prism.fit()
    
    # we wrote a debugging method method for your convinience
    # MAKE SURE TO COMMENT OUT BEFORE SUBMITTING
    printRules(rules,label)

    # Expected output for SEng474 and CSc 578D
    print rules

    # Expected output for CSc 578D
    # print p
