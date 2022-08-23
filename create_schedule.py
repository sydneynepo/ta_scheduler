# takes feedback from a google form and parses the resulting csv file

# to get started, make sure you've installed the following packages using pip:
#  - tkinter

# @author Sydney Nepo
# @author Jackson Parsells

# use tkinter to make it interactive baybeee
import tkinter as tk

import os
import random
from queue import PriorityQueue

# for csv parsing
# csv expected format:
import csv

# constants for time stuff ig
OFFICE_HOUR_BLOCK_LENGTH_HOURS = 1.25
LAB_BLOCK_LENGTH_HOURS = 1.25
LAB_LEAD_EXTRA_HOURS = 1
GRADING_HOURS = 1

from enum import Enum
 
class blockTimes(Enum):
    NINE_AM = 0
    TEN_THIRTY_AM = 1
    TWELVE_PM = 2
    ONE_THIRTY_PM = 3
    THREE_PM = 4
    FOUR_THIRTY_PM = 5
    SIX_PM = 6
    SEVEN_THIRTY_PM = 7
    NINE_PM = 8


# classes for block and student
class block:
    """
    block object
    """
    def __init__(self, id):
        self.id = id
        self.committedTAs = [] # list of TAs who have committed to this block
        self.availableTAs = [] # list of TAs who are available to work on this block
        self.isFull = False # whether or not this block is full

    def assignTAs(self):
        count = len(self.availableTAs)
        while not self.isFull:
            count -= 1
            i = random.randrange(len(self.availableTAs))
            ta = self.availableTAs[i]
            self.addCommittedTA(ta)
            if count == 0:
                print "could not fill block: " + self.id
                break

    
    def addCommittedTA(self, ta):
        if ta.addCommittedBlock(self, OFFICE_HOUR_BLOCK_LENGTH_HOURS):
            self.committedTAs.append(ta)
            self.removeAvailableTA(ta)
        else:
            print "could not add " + ta.name + " to " + self.id
    
        if len(self.committedTAs) == 2:
            self.isFull = True
    
    def removeCommittedTA(self, ta):
        self.committedTAs.remove(ta)
        self.addAvailableTA(ta)
        
        ta.removeCommittedBlock(self, OFFICE_HOUR_BLOCK_LENGTH_HOURS)
        
        if len(self.committedTAs) < 2:
            self.isFull = False
    
    def addAvailableTA(self, ta):
        self.availableTAs.append(ta)

    def removeAvailableTA(self, ta):
        self.availableTAs.remove(ta)

    def numAvailableTAs(self):
        return len(self.availableTAs)

    def findAllAvailableTAs(self, TAs):
        day,time = self.id.split(' ', 1)
        time = int(time)
        for ta in TAs:
            for aBlockTime in ta.availableBlocks:
                if aBlockTime.value == time:
                    for weekDay in ta.availableBlocks[aBlockTime]:
                        if weekDay == day:
                            self.addAvailableTA(ta)

    def printAvailableTAs(self):
        print self.id + ": " 
        for ta in self.availableTAs:
            print(ta.name),
        print ""

    def printCommittedTAs(self):
        print self.id + ": " 
        for ta in self.committedTAs:
            print(ta.name),
        print ""

            

class student:
    """
    student object
    """
    def __init__(self, name, minHours, maxHours, timeAvailabilityMap, willingnessToLeadLab, isNewTA, isWillingToHoldVirtualOfficeHours, preferences):
        self.name = name
        self.minHours = minHours
        self.maxHours = maxHours
        self.currentHours = 0 # "accumulated" hours for each TA
        self.availableBlocks = timeAvailabilityMap # list of blocks that are available to work on
        self.committedBlocks = [] # list of blocks that this student has committed to
        self.isLabLead = False
        self.willingnessToLeadLab = willingnessToLeadLab
        self.isWillingToHoldVirtualOfficeHours = isWillingToHoldVirtualOfficeHours
        self.isNewTA = isNewTA
        self.needsShift = False
        self.canAddShift = True
        self.preferences = preferences
    
    def addCommittedBlock(self, block, hours):
        if self.canAddShift == True:
            self.currentHours += hours
            self.committedBlocks.append(block)
            if self.currentHours + OFFICE_HOUR_BLOCK_LENGTH_HOURS + GRADING_HOURS > self.maxHours:
                self.canAddShift = False
            return True
        else:
            return False
    
    def removeCommittedBlock(self, block, hours):
        self.committedBlocks.remove(block)
        self.currentHours -= hours
        self.canAddShift = True

# actual functions :")

def get_csv_fields(csv_file_name):
    """
    construct a student object
    """
    students = []

    with open(csv_file_name, 'r') as csvfile:
        #  read each field from the csv file and construct a student object for each row
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            # skip the header row
            if i == 0:
                continue

            # destructure row into variables
            name = row[1]
            minHours = int(row[2])
            maxHours = int(row[3])
            timeAvailability1 = row[4].split(", ", 7)
            timeAvailability2 = row[5].split(", ", 7)
            timeAvailability3 = row[6].split(", ", 7)
            timeAvailability4 = row[7].split(", ", 7)
            timeAvailability5 = row[8].split(", ", 7)
            timeAvailability6 = row[9].split(", ", 7)
            timeAvailability7 = row[10].split(", ", 7)
            timeAvailability8 = row[11].split(", ", 7)
            timeAvailability9 = row[12].split(", ", 7)
            isWillingToHoldVirtualOfficeHours = row[13]
            isNewTA = row[14]
            willingnessToLeadLab = row[15]
            preferences = row[17]

            # construct a student object
            timeAvailabilityMap = {
                blockTimes.NINE_AM: timeAvailability1,
                blockTimes.TEN_THIRTY_AM: timeAvailability2,
                blockTimes.TWELVE_PM: timeAvailability3,
                blockTimes.ONE_THIRTY_PM: timeAvailability4,
                blockTimes.THREE_PM: timeAvailability5,
                blockTimes.FOUR_THIRTY_PM: timeAvailability6,
                blockTimes.SIX_PM: timeAvailability7,
                blockTimes.SEVEN_THIRTY_PM: timeAvailability8,
                blockTimes.NINE_PM: timeAvailability9
            }
            currStudent = student(name, minHours, maxHours, timeAvailabilityMap, willingnessToLeadLab, isNewTA, isWillingToHoldVirtualOfficeHours, preferences)
            
            # add the student to the list of students
            students.append(currStudent)

    return students

def load_calendar():
    pass

def initBlocks(TAs):
    allBlocks = []
    for i in range(0,7):
        for j in range(0,9):
            id = ""
            if i == 0:
                id = "Sunday" + " " + str(j) 
            if i == 1:
                id = "Monday" + " " + str(j) 
            if i == 2:
                id = "Tuesday" + " " + str(j) 
            if i == 3:
                id = "Wednesday" + " " + str(j)
            if i == 4:
                id = "Thursday" + " " + str(j)  
            if i == 5:
                id = "Friday" + " " + str(j)
            if i == 6:
                id = "Saturday" + " " + str(j)
            aBlock = block(id)
            aBlock.findAllAvailableTAs(TAs)
            allBlocks.append(aBlock)
    
    return allBlocks

def retrieveBlock(blocks, blockID):
    for block in blocks:
        if (block.id == blockID):
            return block
    return None

def prioritizeBlocks(blocks):
    q = PriorityQueue()
    for block in blocks:
        day,time = block.id.split(' ', 1)
        if day != "Saturday":
            q.put(block.numAvailableTAs, block)
    
    return q

def retrieveStudent(students, name):
    for student in students:
        if (student.name == name):
            return student
    return None

def manuallyAssignStudent(blocks, students, name, blockID):
    student = retrieveStudent(students, name)
    for block in blocks:
        if block.id == blockID:
            block.addCommittedTA(student)
            break

def automateSchedule(p):
    while not p.empty():
        currBlock = p.get()
        #print currBlock.id
        #currBlock.assignTAs()

def babyAutomateSchedule(blocks):
    for aBlock in blocks:
        day,time = aBlock.id.split(' ', 1)
        if day != "Saturday":
            aBlock.assignTAs()


# main(e)

def main():
    """
    beep boop, fill in main here
    """
    print "hi"
    students = get_csv_fields('TAAvailability.csv')

    # init list of blocks (don't forget to add labs!)
    OHBlocks = initBlocks(students)

    # for sanity check
 #   for aBlock in allBlocks:
 #       aBlock.printAvailableTAs()

 # manually set certain TF hours, and lab leads
    #manuallyAssignStudent(OHBlocks, students, "Caleb Arzt", "Monday 1")

    babyAutomateSchedule(OHBlocks)

    #priority = prioritizeBlocks(OHBlocks)
    #aBlock = priority.get()
    #print("The type is : ", type(aBlock))
    #print block.id
    #automateSchedule(priority)
  
    for aBlock in OHBlocks:
        aBlock.printCommittedTAs()
    

    # find block with least amount of available TAs, and on that block
        # assign 2 TAs by first checking that they can add it 

    


if __name__ == '__main__':
    main()
