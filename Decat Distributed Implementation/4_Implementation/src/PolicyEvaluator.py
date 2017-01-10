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
        self.readObjectConditions = policy['readObjectConditions']
        self.writeObjectConditions = policy['writeObjectConditions']
        self.writeObjectUpdates = policy['writeObjectUpdates']
        self.readObjectUpdates = policy['readObjectUpdates']
        self.predictionFailed= False

    def isPolicySatisfied(self, readObjectRecord, writeObjectRecord, action, readAttrs, updates):
        self.predictionFailed = False
        readAttrs['readObject'] = {}
        readAttrs['writeObject'] = {}
        # print()
        # print("action : "  + str(action))
        # print("WriteObjectRecord is  "+ str(writeObjectRecord))

        # print("readObjectRecord is  "+ str(readObjectRecord))
        

        updates['readObject'] = {'id':readObjectRecord['objectId']}
        updates['writeObject'] = {'id':writeObjectRecord['objectId']}
        if (action == self.action and self.isReadObjPolicySatisfied(readObjectRecord, readAttrs['readObject'])
          and self.isWriteObjPolicySatisfied(writeObjectRecord, readAttrs['writeObject'])):
            self.generateReadObjectUpdates(readObjectRecord, writeObjectRecord, updates['readObject'])
            self.generateWriteObjectUpdates(writeObjectRecord, readObjectRecord, updates['writeObject'])
            # print("updates : " + str(updates))
            result = True
        else:
            result = False

        if self.predictionFailed:
            tmp = updates['readObject']
            updates['readObject'] = updates['writeObject']
            updates['writeObject'] = tmp

            tmp = updates['readObject']['id']
            updates['readObject']['id'] = updates['writeObject']['id']
            updates['writeObject']['id'] = tmp

        return result


    def isReadObjPolicySatisfied(self, readObjectRecord, readAttrs):
        for attribute, condition in self.readObjectConditions.items():
            if (attribute in readObjectRecord):
                readAttrs[attribute] = readObjectRecord[attribute]
                if not self.checkAttributeCondition(attribute, condition, readObjectRecord):
                    return False
            else :
                self.predictionFailed = True
                return self.isWriteObjPolicySatisfied(readObjectRecord, readAttrs)
        return True

    def isWriteObjPolicySatisfied(self, writeObjectRecord, readAttrs):
        for attribute, condition in self.writeObjectConditions.items():
            if (attribute in writeObjectRecord):
                readAttrs[attribute] = writeObjectRecord[attribute]
                if not self.checkAttributeCondition(attribute, condition, writeObjectRecord):
                    return False
            else :
                self.predictionFailed = True
                return self.isReadObjPolicySatisfied(writeObjectRecord, readAttrs)
        return True

    def checkAttributeCondition(self, attribute, condition, record):
        if (condition[0] == "<"):
            return int(record[attribute]) < int(condition[1:])
        elif (condition[0] == ">"):
            return int(record[attribute]) > int(condition[1:])
        else:
            return record[attribute] == condition

    def generateReadObjectUpdates(self, subjectRecord, resourceRecord, updates):
        for attribute, update in self.readObjectUpdates.items():
            if attribute in subjectRecord:
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
            else:
                self.predictionFailed = True
                return self.generateReadObjectUpdates(resourceRecord, subjectRecord, updates)

    def generateWriteObjectUpdates(self, resourceRecord, subjectRecord, updates):
        for attribute, update in self.writeObjectUpdates.items():
            if attribute in resourceRecord:
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
            else:
                self.predictionFailed = True
                return self.generateWriteObjectUpdates(subjectRecord, resourceRecord, updates) 


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

    def isAnyPolicySatisfied(self, readObjectRecord, writeObjectRecord, action, readAttrs, updates):
        updates.clear()
        readAttrs.clear()
        #print(readObjectRecord)
        #print(writeObjectRecord)
        #print()
        for policy in self.policies:
            if policy.isPolicySatisfied(readObjectRecord, writeObjectRecord, action, readAttrs, updates):
                return True
        return False