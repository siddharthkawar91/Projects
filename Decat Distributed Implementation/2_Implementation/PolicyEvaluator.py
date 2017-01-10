import json


"""
This class is used to test whether a subject and resource record satisfy this policy or not 
based on subject and resource conditions

refer isPolicySatisfied()
Updates the object 'readAttrs' with the attributes that were read for this evaluation
Updates the object 'updates' with the updates that should be applied to the record
"""
class Policy:
    def __init__(self, policy):
        self.id = policy['id']
        self.name = policy['name']
        self.action = policy['action']
        self.subjectConditions = policy['subjectConditions']
        self.resourceConditions = policy['resourceConditions']
        self.subjectUpdates = policy['subjectUpdates']
        self.resourceUpdates = policy['resourceUpdates']

    def isPolicySatisfied(self, subjectRecord, resourceRecord, action, readAttrs, updates):
        readAttrs['subject'] = {}
        readAttrs['resource'] = {}
        updates['subject'] = {'subjectId':subjectRecord['subjectId']}
        updates['resource'] = {'resourceId':resourceRecord['resourceId']}
        if (action == self.action and self.isSubjectPolicySatisfied(subjectRecord, readAttrs['subject'])
          and self.isResourcePolicySatisfied(resourceRecord, readAttrs['resource'])):
            self.generateSubjectUpdates(subjectRecord, resourceRecord, updates['subject'])
            self.generateResourceUpdates(resourceRecord, subjectRecord, updates['resource'])
            return True
        else:
            return False


    def isSubjectPolicySatisfied(self, subjectRecord, readAttrs):
        for attribute, condition in self.subjectConditions.items():
            readAttrs[attribute] = subjectRecord[attribute]
            if not self.checkAttributeCondition(attribute, condition, subjectRecord):
                return False
        return True

    def isResourcePolicySatisfied(self, resourceRecord, readAttrs):
        for attribute, condition in self.resourceConditions.items():
            readAttrs[attribute] = resourceRecord[attribute]
            if not self.checkAttributeCondition(attribute, condition, resourceRecord):
                return False
        return True

    def checkAttributeCondition(self, attribute, condition, record):
        if (condition[0] == "<"):
            return int(record[attribute]) < int(condition[1:])
        elif (condition[0] == ">"):
            return int(record[attribute]) > int(condition[1:])
        else:
            return record[attribute] == condition

    def generateSubjectUpdates(self, subjectRecord, resourceRecord, updates):
        for attribute, update in self.subjectUpdates.items():
            if update == "++":
                updates[attribute] = int(subjectRecord[attribute]) + 1
            elif update == "--":
                updates[attribute] = int(subjectRecord[attribute]) - 1
            elif update[0:2] == "$s":
                subjectAttr = update[update.find('.') + 1:]
                updates[attribute] = subjectRecord[subjectAttr]
            elif update[0:2] == "$r":
                resourceAttr = update[update.find('.') + 1:]
                updates[attribute] = resourceRecord[resourceAttr]
            else:
                updates[attribute] = update

    def generateResourceUpdates(self, resourceRecord, subjectRecord, updates):
        for attribute, update in self.resourceUpdates.items():
            if update == "++":
                updates[attribute] = int(resourceRecord[attribute]) + 1
            elif update == "--":
                updates[attribute] = int(resourceRecord[attribute]) - 1
            elif update[0:2] == "$s":
                subjectAttr = update[update.find('.') + 1:]
                updates[attribute] = subjectRecord[subjectAttr]
            elif update[0:2] == "$r":
                resourceAttr = update[update.find('.') + 1:]
                updates[attribute] = resourceRecord[resourceAttr]
            else:
                updates[attribute] = update 



"""
This class is used to test whether a subject and resource record satisfy any policy in our
list of policies based on subject and resource conditions

refer isAnyPolicySatisfied()
Updates the object 'readAttrs' with the attributes that were read for this evaluation by the satisfied policy
Updates the object 'updates' with the updates that should be applied to the record according to the satisfied policy
"""
class PolicyEvaluator:
    def __init__(self, policyFilename):
        policyFile = open(policyFilename, "r")
        policiesJson = json.load(policyFile)
        self.policies = self.loadPolicies(policiesJson)

    def loadPolicies(self, policiesJson):
        policies = []
        for policy in policiesJson:
            policies.append(Policy(policy))
        return policies

    def isAnyPolicySatisfied(self, subjectRecord, resourceRecord, action, readAttrs, updates):
        for policy in self.policies:
            if policy.isPolicySatisfied(subjectRecord, resourceRecord, action, readAttrs, updates):
                return True
        return False