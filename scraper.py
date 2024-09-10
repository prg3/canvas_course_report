#!/usr/bin/env python3
import math, pickle, datetime, json, requests, os


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

outfolder = "outfolder/"
if not os.path.isdir(outfolder):
    os.makedirs(outfolder)


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

courses = {}

if response.status_code == 200:
    for course in response.json()['data']['allCourses']:
        # print(course['_id'])
        # print(course['name'])
        courses[course['_id']] = {
            "name" : course['name'],
            "assignments" : []
        }

        for a in course['assignmentsConnection']['nodes']:
            assignmentId = a['_id']
            assignmentDetail = requests.get(url = baseUrl + "/api/v1/courses/" + course['_id'] + "/assignments/" + assignmentId, headers=headers)

            # assignmentDetail = requests.get(url = baseUrl + "/api/v1/courses/" + course['_id'] + "/assignments/" + assignmentId + "/submissions/" + studentId, headers=headers)
            if assignmentDetail.status_code == 200:
                assignment = json.loads(assignmentDetail.text)
                courses[course['_id']]['assignments'].append(assignment)

print(json.dumps(courses))

f = open("today.pickle", 'wb')
pickle.dump(courses, f)
