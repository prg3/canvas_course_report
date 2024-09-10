#!/usr/bin/env python3

import requests
import json
import datetime
import math


class courseType:
    def __init__(self, name):
        self.id = ""
        self.name = name
        self.assignments = []
        self.assignmentTotal = 0
        self.assignmentDone = 0
        self.assignmentPending = 0

    def addAssignment(self):
        self.assignmentTotal = self.assignmentTotal + 1

    def addAssignmentDone(self):
        self.assignmentDone = self.assignmentDone + 1

    def addAssignmentPending(self):
        self.assignmentPending = self.assignmentPending + 1

    def setPoints(self, points):
        self.points = points

    def getName(self):
        return(self.name)

    def getAssignmentCount(self):
        return(self.assignmentTotal)

    def getAssignmentDone(self):
        return(self.assignmentDone)

    def getAssignmentPending(self):
        return(self.assignmentPending)

    def getAssignmentLeft(self):
        return(self.assignmentTotal - self.assignmentDone)

    def getPercentDone(self):
        return ((self.assignmentDone + self.assignmentPending) / self.assignmentTotal)

    def getPoints(self):
        return (self.points)

assignmentData = {
    "name" : "",
    "complete" : False,
}

now = datetime.datetime.now()
end = datetime.datetime(2023, 6, 1)

delta = end - now

courseData = {}

token = open("token.secret", "r").read().rstrip()
baseUrl = "https://eics.instructure.com"
graphQLUrl = baseUrl + "/api/graphql"
auth_header = 'Bearer ' + token
headers = {'Authorization': auth_header}

selfDetail = requests.get(url = baseUrl + "/api/v1/users/self/", headers=headers)
selfID = str(json.loads(selfDetail.text)['id'])
observeeDetail = requests.get(url = baseUrl + "/api/v1/users/" + selfID  + "/observees", headers=headers)


studentId = str(json.loads(observeeDetail.text)[0]['id'])

# headers = { 
#     "Accept": "application/json",
#     "Content-Type": "application/json",
#     "Authorization": "BEARER "+ str(token),
# }

query = """{
    allCourses {
        courseCode
        _id
        name
        assignmentsConnection {
        nodes {
            _id
            name
            expectsSubmission
            gradingType
            pointsPossible
            gradeGroupStudentsIndividually
            hasSubmittedSubmissions
        }
        }
        }
}"""

data = {"query" : query}

response = requests.post(url=graphQLUrl, headers=headers, data=data)

f = open("graphql.out", "w")
f.write(json.dumps(response.json()))
f.close()

if response.status_code == 200:
    for course in response.json()['data']['allCourses']:
        # print(course['courseCode'])
        courseId = course['_id']
        courseData[courseId] = courseType(course['name'])

        for a in course['assignmentsConnection']['nodes']:
            # print(a['name'])
            assignmentId = a['_id']
            assignmentDetail = requests.get(url = baseUrl + "/api/v1/courses/" + courseId + "/assignments/" + assignmentId + "/submissions/" + studentId, headers=headers)
            if assignmentDetail.status_code == 200:
                f = open(courseId + "-" + assignmentId + ".out", "w")
                aD = json.loads(assignmentDetail.text)
                f.write(json.dumps(aD))
                f.close()
                # print(aD['workflow_state'])
                # if "score" in aD.keys():
                #     print(aD['score'])
                if aD['workflow_state'] in [ "graded"]:
                    # print (aD['score'])
                    if aD['score']:
                        if aD['score'] > 0:
                            courseData[courseId].addAssignmentDone()
                if aD['workflow_state'] in [  "pending_review", "submitted" ]:
                    courseData[courseId].addAssignmentPending()
            if a['expectsSubmission']:
                courseData[courseId].addAssignment()

for i in courseData:
    data = courseData[i]
    print(data.getName())
    print("Assignments submitted : " + str(data.getAssignmentDone()))
    print("Assignments pending   : " + str(data.getAssignmentPending()))
    print("Assignment total      : " + str(data.getAssignmentCount()))
    print("Percent complete      : {:2.1%}".format(data.getPercentDone()))
    print("Assignments per Day   : {:2.1f}".format((data.getAssignmentCount() - (data.getAssignmentDone() + data.getAssignmentPending())) / delta.days * 7/5 ))
    print("Assignments per Week  : {:2.1f}".format((data.getAssignmentCount() - (data.getAssignmentDone() + data.getAssignmentPending())) / math.trunc(delta.days / 7 )))
    print("\n")

totals = {
    "aD" : 0,
    "aC" : 0,
    "aP" : 0
}

for i in courseData:
    data = courseData[i]
    totals['aD'] = data.getAssignmentDone() + totals['aD']
    totals['aP'] = data.getAssignmentPending() + totals['aP']    
    totals['aC'] = data.getAssignmentCount() + totals['aC']

print("Total submitted       : " + str(totals['aD']))
print("Total pending         : " + str(totals['aP']))
print("Total left            : " + str(totals['aC'] - (totals['aD'] + totals['aP'])))
print("Total total           : " + str(totals['aC']))
print("Percent complete      : {:2.1%}".format((totals['aD'] + totals['aP']) / totals['aC']))
print("Assignments per Day   : {:2.1f}".format((totals['aC'] - (totals['aD'] + totals['aP'])) / delta.days * 7/5))
print("Assignments per Week  : {:2.1f}".format((totals['aC'] - (totals['aD'] + totals['aP'])) / math.trunc(delta.days / 7 )))
