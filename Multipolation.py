#MenuTitle: MultipolationOrg
#-*- coding: utf-8 -*-
__doc__ = """
Advanced interpolation with infinite axes.
Author: Manuel von Gebhardi (CC-BY-SA)
Co-Authors: Matthias Visser, ...

TODO:
o Integration as a Custom Parameter in Glyphs Font Info (getting rid of the extra spec file)
o Interface (Setup, Slider, Knobs, ...)
o Full integration of complex axes (axes relations, math, switches, ...)
o Direct export as a variable  font (though the variable font spec has to catch up with features)

"""

from Foundation import *
import GlyphsApp
import vanilla
import math
import os.path

import inspect
import copy

import json
from pprint import pprint
import copy

from random import randint
import ast  # string to list


Doc = Glyphs.currentDocument
Font = Glyphs.font  # frontmost font

jsonfilename = "_multipolation-spec.json"

# New Local Interpolation Custom Parameter
# print =;{0.5,1}:1,0.5};include:A
LocalGlyphInterpolations = []
LocalGlyphInterpolations += [""]


# Functions


def string_to_list(x):
	return ast.literal_eval(x)


def redefinelist(x):
	return string_to_list(str(x))


def map(value, inMin, inMax, outMin, outMax):
	# Figure out how 'wide' each range is
	leftSpan = inMax - inMin
	rightSpan = outMax - outMin

	# Convert the left range into a 0-1 range (float)
	valueScaled = float(value - inMin) / float(leftSpan)

	# Convert the 0-1 range into a value in the right range.
	return outMin + (valueScaled * rightSpan)


# convert unicode json data


def byteify(input):
	if isinstance(input, dict):
		return {byteify(key): byteify(value)
				for key, value in input.iteritems()}
	elif isinstance(input, list):
		return [byteify(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input


def func(a, b, c):
	frame = inspect.currentframe()
	args, _, _, values = inspect.getargvalues(frame)
	# print 'function name "%s"' % inspect.getframeinfo(frame)[2]
	for i in args:
		print "	%s = %s" % (i, values[i])
	return [(i, values[i]) for i in args]


def AddInstance(myname, myfilters=False):
	newInstance = GSInstance()
	newInstance.active = True  # Activate_New_Instances
	newInstance.name = myname  # prefix + "{0:.0f}".format( thisWeight )
	newInstance.weightValue = 1
	newInstance.widthValue = 1
	newInstance.isItalic = False
	newInstance.isBold = False

	# print "\nAdd Instance"
	if myfilters:
		AddCustomParameter(newInstance, myfilters)

	Glyphs.font.addInstance_(newInstance)


def AddCustomParameter(myInstance, myfilters=False):
	if myfilters:
		if myfilters[0]:
			# print myfilters
			tempArray = myfilters[0].split("::")

			myfilters_Count = len(myfilters)

			for k in range(myfilters_Count):
				tempArray = myfilters[k].split("::")
				#myInstance.customParameters[tempArray[0]] = tempArray[1]
				cp = GSCustomParameter.alloc().init()
				cp = GSCustomParameter(tempArray[0], tempArray[1])
				myInstance.customParameters.append(cp)

	# print "	Filters Added ", myInstance.customParameters


def getGSObjectIndex(thisArray, name):
	k = 0
	for child in thisArray:
		if (name == child.name):
			return k
		k += 1


def sumSelDictValues(thisArray, selectionArray, childsvalue):
	sum = [0.0, 0.0]  # xy
	sum_string = ["", ""]

	for selection in selectionArray:
		for k in range(len(sum)):
			sum[k] += thisArray[selection][childsvalue][k]
			sum_string[k] += " + " + str(thisArray[selection][childsvalue][k])

	# print ""
	# print "sum_x =", sum_string[0], "=", sum[0]
	# print "sum_y =", sum_string[1], "=", sum[1]
	# print ""

	return sum


# def insertInArrayAtposition(thisArray, element, position):
#	print "insertInArrayAtposition", thisArray, position, element
#	print type(thisArray)
#	thisArray.splice(position, 0, element);


def convertmyList2Array(list):
	newarray = []
	for elementstr in list:
		#insertInArrayAtposition(newarray, elementstr, )
		newarray.append(elementstr)
	return newarray


def CheckIfValuesSequel(thisArray):
	for name in thisArray:
		sum += thisArray[selection][childsvalue]
	return sum


def getMasterNames(excludeStr):  # * #excludeStr="whatever"
	MasterNameArray = []
	excludeStr = [excludeStr]
	for k in range(len(Font.masters)):
		name = [byteify(Font.masters[k].name)]
		if (name != excludeStr):
			MasterNameArray += name
	return MasterNameArray


def getInstanceMasterValuesCalcOrder(data):
	MastersWithChilds = getMasterWithChildren(data)
	MastersWithoutChildsArray = getMasterWithOutChildren(data)

	OrderArrayBefore = convertmyList2Array(MastersWithChilds)
	OrderArrayBefore = list(reversed(OrderArrayBefore))
	OrderArrayBeforeStr = str(OrderArrayBefore)
	OrderAsArray = OrderArrayBefore

	k = 0
	NewOrderAsArray = OrderAsArray
	for MasterWithChildsName in MastersWithChilds:
		children = data["MasterSetupMapping"][MasterWithChildsName][2]

		for MasterWithChildsName2 in MastersWithChilds:

			if MasterWithChildsName2 in children:

				OrderAsArray = NewOrderAsArray

				firstIndex = OrderAsArray.index(MasterWithChildsName2)
				secondIndex = OrderAsArray.index(MasterWithChildsName)

				if (firstIndex > secondIndex):

					k += 1
					# print k
					# print "OrderAsArrayBefore", OrderAsArray
					OrderAsArray.insert(
						firstIndex, OrderAsArray.pop(secondIndex))

					# print "OrderAsArrayAfter", OrderAsArray

					#, "(contains:", MasterWithChildsName2, children
					# print OrderAsArray
					# Update Order #array.insert(firstIndex,
					# array.pop(oldindex))
					NewOrderAsArray = OrderAsArray

	# InstanceMasterValuesCalcOrder = MastersWithChilds#.update({MasterWithChildsName:1})
	# print ""
	# print "	   Before", OrderArrayBeforeStr
	# print "	   After", OrderAsArray

	# print "	   Complete", MastersWithoutChildsArray + OrderAsArray

	return MastersWithoutChildsArray + OrderAsArray


def getMasterWithChildren(data):  # previous name: getMasterWithChildren
	MasterWithChildren = {}
	k = 0
	for mastername in data["MasterSetupMapping"]:
		if not mastername.startswith("_"):  # exclude comments, etc.

			# print
			# print mastername, "mastername"
			# print len(data["MasterSetupMapping"][mastername]), 'len(data["MasterSetupMapping"][mastername])'
			# print data["MasterSetupMapping"][mastername],
			# 'data["MasterSetupMapping"][mastername]'
			if (len(data["MasterSetupMapping"][mastername]) > 2):  # only the ones with children
				children = data["MasterSetupMapping"][mastername][2]



				if (children == "All"):
					# excludes this mastername
					children = getMasterNames(mastername)
					data["MasterSetupMapping"][mastername][2] = children

				# Onwards we have all Masters with Children (mastername)

				MasterWithChildren.update({mastername: k})  # k
				k += 1  # initial random order

				#["Serifinner","Serifweight","Serifangle"]
				#[""Bold"Serifinner","Serifweight","Serifangle"]

				# Set Order of calculations
				# Root Exception "all" needs to be excecuted last
	return MasterWithChildren


def getMasterWithOutChildren(data):  # previous name: getMasterWithChildren
	MasterWithOutChildrenArray = []
	k = 0
	for mastername in data["MasterSetupMapping"]:
		if not mastername.startswith("_"):  # exclude comments, etc.
			# only the ones with children
			if (not len(data["MasterSetupMapping"][mastername]) > 2):
				MasterWithOutChildrenArray += [str(mastername)]

	return MasterWithOutChildrenArray





def convert2LocalInterpolation(data):

	# Base Settings // Fallback Setting / Base Setting // allows for less repitition in the spec file
	# ----------------------
	# Check if there are fallback values
	base_setting = True
	try:
		_base_setting = data["InstancesSetup"]["_base_setting"]
	except:
		try:
			data["InstancesSetup"]["_base_setting"] = data["InstancesSetup"]["_fallback_values"]
		except:
			try:
				data["InstancesSetup"]["_base_setting"] = data["InstancesSetup"]["Default"]
			except:
				try:
					data["InstancesSetup"]["_base_setting"] = data["InstancesSetup"]["Regular"]
				except:
					base_setting = False
					# print "ERROR - please one of the following Instances: Regular, Default, _fallback_values"
					# TODO: The setting of the Root master could also be set up as the base setting though

	if not ("#All" in data["InstancesSetup"]["_base_setting"]):
		tempdata = copy.deepcopy(data)
		del data["InstancesSetup"]["_base_setting"]
		data["InstancesSetup"]["_base_setting"] = {}
		data["InstancesSetup"]["_base_setting"]["#All"] = tempdata["InstancesSetup"]["_base_setting"]
	# ----------------------
	# END - Base Settings


	# Go through all Instances
	for instancename in data["InstancesSetup"]:

		forced_Setup_on_all_Groups = False

		for charGroupName in data["InstancesSetup"][instancename]:
			if charGroupName == "_All_Force":
				#tempdata = copy.deepcopy(data)
				#del data["InstancesSetup"][instancename]
				#data["InstancesSetup"][instancename] = {}
				forced_Setup_on_all_Groups = tempdata["InstancesSetup"][instancename]["_All_Force"]
				forced_Setup_on_all_Groups = copy.deepcopy(forced_Setup_on_all_Groups)





		# ignore all but Master-Axis (without _) and CharGroups (#)
		if not instancename.startswith("_"):


			# If there are no local Interpolations == CharGroups
			# > Restructure > put axis-interpolation infos into #All


			if not ("#All" in data["InstancesSetup"][instancename]):

				tempdata = copy.deepcopy(data)
				del data["InstancesSetup"][instancename]
				data["InstancesSetup"][instancename] = {}

				data["InstancesSetup"][instancename]["#All"] = tempdata["InstancesSetup"][instancename]


			# Apply the values of the "_base_setting" instance to all other Groups if not otherwise specified
			if base_setting:
				if not (instancename == "_base_setting"):
					tempdata = copy.deepcopy(data)
					del data["InstancesSetup"][instancename]["#All"]
					data["InstancesSetup"][instancename]["#All"] = {}

					data["InstancesSetup"][instancename]["#All"] = tempdata["InstancesSetup"]["_base_setting"]["#All"]
					# overwrite with original settings, if they exist
					for mastername in tempdata["InstancesSetup"][instancename]["#All"]:
						data["InstancesSetup"][instancename]["#All"][mastername] = tempdata["InstancesSetup"][instancename]["#All"][mastername]








			# Set fallback values for other char groups
			if base_setting:
				for charGroupName in data["InstancesSetup"]["_base_setting"]:
					if not (charGroupName == "#All"):

						tempdata = copy.deepcopy(data)
						try:
							del data["InstancesSetup"][instancename][charGroupName]
							charGroupName_does_exist = True
						except: #does not exist, assign directly
							charGroupName_does_exist = False
							pass
						data["InstancesSetup"][instancename][charGroupName] = {}
						data["InstancesSetup"][instancename][charGroupName] = tempdata["InstancesSetup"]["_base_setting"][charGroupName]


						# overwrite with original settings, if they exist
						if charGroupName_does_exist:
							for mastername in tempdata["InstancesSetup"][instancename][charGroupName]:
								data["InstancesSetup"][instancename][charGroupName][mastername] = tempdata["InstancesSetup"][instancename][charGroupName][mastername]

						# Overwrite Chargroup Defaults by Force
						if forced_Setup_on_all_Groups:
							for mastername in forced_Setup_on_all_Groups:
								data["InstancesSetup"][instancename][charGroupName][mastername] = forced_Setup_on_all_Groups[mastername]


			# Apply the values of #All to all other Groups if not otherwise
			# specified
			for charGroupName in data["InstancesSetup"][instancename]:
				if not (charGroupName == "#All"):
					if not (charGroupName == "_All_Force"):
						tempdata = copy.deepcopy(data)
						del data["InstancesSetup"][instancename][charGroupName]
						data["InstancesSetup"][instancename][charGroupName] = {}

						data["InstancesSetup"][instancename][charGroupName] = tempdata[
							"InstancesSetup"][instancename]["#All"]

						for mastername in tempdata["InstancesSetup"][instancename][charGroupName]:
							data["InstancesSetup"][instancename][charGroupName][mastername] = tempdata[
								"InstancesSetup"][instancename][charGroupName][mastername]




def convertNormal2XYinterpolation(data):
	# only for first two values
	childs = False

	for mastername in data["MasterSetupMapping"]:
		# print ""
		# print mastername
		if not mastername.startswith("_"):
			values = data["MasterSetupMapping"][mastername]
			if (len(values) > 2):  # gets childs
				childs = values.pop(-1)
				# print childs, "childs"
			else:
				childs = False

			interpolrange = values

			# convert [0,1] to [[0,1],[0,1]]
			if not (type(interpolrange[0]) == list):
				newvalues = [interpolrange, interpolrange]
				# print "append childs:", childs, newvalues
			else:
				newvalues = interpolrange

			if (childs):
				newvalues.append(childs)
				# print newvalues
			data["MasterSetupMapping"][mastername] = newvalues

	for instancename in data["InstancesSetup"]:

		if not instancename.startswith("_"):
			# print ""
			# print instancename
			for charGroupName in data["InstancesSetup"][instancename]:



				if not charGroupName.startswith("_"):
					# print charGroupName
					for mastername in data["InstancesSetup"][instancename][charGroupName]:

						if not mastername.startswith("_"):

							# check for min max expressions
							# TODO -> do a convertValueExpressions function after this conversion.. so that it is independed
							#valuestr = str(data["InstancesSetup"][instancename][charGroupName][mastername])
							interpolvals = data["InstancesSetup"][
								instancename][charGroupName][mastername]
							# print "val", interpolvals, type(interpolvals)
							# interpolvals = eval(valuestr) #eval allows math
							# operations!
							if not (type(interpolvals) == list):
								valuestr = str(interpolvals)
								tempMin = str(data["MasterSetupMapping"][
											  mastername][0][0])
								tempMax = str(data["MasterSetupMapping"][
											  mastername][0][1])
								tempHalf = str(
									map(0.5, 0, 1, eval(tempMin), eval(tempMax)))
								#> convert to number first!!!

								# print "tempHalf", tempHalf

								# TODO: Clean up / write a function for this
								valuetemp = valuestr.replace("parent", tempMin)
								valuestr = str(valuetemp)
								valuetemp = valuestr.replace("none", tempMin)
								valuestr = str(valuetemp)
								valuetemp = valuestr.replace("min", tempMin)
								valuestr = str(valuetemp)

								valuetemp = valuestr.replace("half", tempHalf)
								# works also for "half" ->		tempMin +
								# ((tempMax - tempMin)/2)
								valuestr = str(valuetemp)

								valuetemp = valuestr.replace("full", tempMax)
								valuestr = str(valuetemp)
								valuetemp = valuestr.replace("max", tempMax)
								valuestr = str(valuetemp)

								valuestr = valuetemp

								interpolval = eval(valuestr)

								data["InstancesSetup"][instancename][charGroupName][
									mastername] = [interpolval, interpolval]
							else:
								# print "xy"
								# print len(interpolvals)
								new_interpolvals = []
								for k in range(len(interpolvals)):
									# print k
									valuestr = str(interpolvals[k])
									tempMin = str(data["MasterSetupMapping"][
												  mastername][k][0])
									tempMax = str(data["MasterSetupMapping"][
												  mastername][k][1])
									tempHalf = str(
										map(0.5, 0, 1, eval(tempMin), eval(tempMax)))

									tempDouble = str(
										map(2, 0, 1, eval(tempMin), eval(tempMax)))

									# print tempMin
									# print tempMax
									# print "tempHalf", tempHalf

									# TODO: Clean up / write a function for
									# this
									valuetemp = valuestr.replace(
										"parent", tempMin)
									valuestr = str(valuetemp)
									valuetemp = valuestr.replace(
										"none", tempMin)
									valuestr = str(valuetemp)
									valuetemp = valuestr.replace(
										"min", tempMin)
									valuestr = str(valuetemp)

									valuetemp = valuestr.replace(
										"half", tempHalf)
									valuestr = str(valuetemp)

									valuetemp = valuestr.replace(
										"double", tempDouble)
									valuestr = str(valuetemp)

									valuetemp = valuestr.replace(
										"full", tempMax)
									valuestr = str(valuetemp)
									valuestr = valuetemp
									valuetemp = valuestr.replace(
										"max", tempMax)
									valuestr = str(valuetemp)
									valuestr = valuetemp

									interpolval = eval(valuestr)
									new_interpolvals += [interpolval]

								# print "new", new_interpolvals
								data["InstancesSetup"][instancename][charGroupName][
									mastername] = [new_interpolvals[0], new_interpolvals[1]]

							# print "mastername", mastername, data["InstancesSetup"][instancename][charGroupName][mastername]
							# print ""

							# if not (type(interpolval[-1]) == int):
							# Local Interpolations!

	# check conversion
	# pprint(data["MasterSetupMapping"])
	# pprint(data["InstancesSetup"])

# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------

# Main Function/Class


class Multipolation(object):

	def __init__(self):
		print "\n\n#0 Init Multipolation"
		print "----------------------------------------------------------------------"
		print "----------------------------------------------------------------------"
		jsonpath = Font.filepath.replace(".glyphs", jsonfilename)

		self.LoadSpecification(jsonpath)

	def LoadSpecification(self, jsonpath):

		print "\n\n#1 Load Specification"
		print "----------------------------------------------------------------------"
		# just for reference in the console
		print "  Spec Filename = ", jsonpath.split("/")[-1]
		# print "  ", jsonpath #prints complete path

		with open(jsonpath) as data_file:
			data = json.load(data_file)

			data = byteify(data)  # convert unicode

		# pprint(data)
		self.SliderInterface(data)

	def SliderInterface(self, data):
		print "\n\n#2 Init Interface"
		print "----------------------------------------------------------------------"
		print "  There are no sliders, nor a basic interface yet. Please edit the .json."
		#-slider = False
		self.Interpolation(data)

	def Interpolation(self, data):
		print "\n\n#3 Interpolate"
		print "----------------------------------------------------------------------"

		# General Settings
		# ------------------
		# ??? ToDo revise: add to spec or delete?
		Activate_New_Instances = True
		Activate_Last_Filter = False
		Add_Masters_as_Instances = False
		# ????


		try:
			General_Custom_Parameter_Before = data["GeneralSetup"]["Filters_general_before"]
		except:
			General_Custom_Parameter_Before = data["GeneralSetup"]["Custom_Parameter_before"]

		#General_Custom_Parameter_Before_Interpolated_Instances = General_Custom_Parameter_Before
		try:
			General_Custom_Parameter_After = data["GeneralSetup"]["Filters_general_after"]
		except:
			General_Custom_Parameter_After = data["GeneralSetup"]["Custom_Parameter_after"]

		# try:
		# 	XY_Interpolation = data["GeneralSetup"]["XY_Interpolation"]
		# except:
		# 	XY_Interpolation = False

		# if (XY_Interpolation):
		#	print "#-- XY Interpolationt =", XY_Interpolation, "#--"

		# check for local/String Interpolations -> and Restructure the Data
		convert2LocalInterpolation(data)

		# I couldn’t make it switchable, so its always on
		convertNormal2XYinterpolation(data)

		#["GlyphsFilterOffsetCurve; 1; 1; 1; 0.5;", "GlyphsFilterRoundCorner; 1; 1;"]

		Instances_reset_all = data["GeneralSetup"][
			"Instances_reset_all"]  # False

		Add_Custom_Parameter = len(General_Custom_Parameter_Before) or len(General_Custom_Parameter_After)  # True #eg Filters
		#print "\n\nAdd_Custom_Parameter:", Add_Custom_Parameter, "\n",General_Custom_Parameter_Before, "\n", General_Custom_Parameter_After, "\n"

		# Init Variables
		# ---------------------

		interpol_array = []
		Instances = Font.instances
		Masters = Font.masters
		Master_Count = len(Masters)
		Instances_Count = len(Instances)
		print "	- Mastercount: ", Master_Count

		# Clear values in the .glyphs file
		#----------------------------------------

		Instance_reset_Values = []

		for k in range(0, Master_Count - 1, 1):
			Instance_reset_Values = Instance_reset_Values + \
				[0.0]  # .append(0.0)

		# Sets each Master as an Instances
		#----------------------------------------

		# ToDo take Master names from specfile or from glyphs file

		if(Add_Masters_as_Instances):
			# Add Root as Instance
			interpol_array.append(
				Instance_reset_Values + ["0 - Root-Master"] + [General_Custom_Parameter_Before])
			#interpol_array.append("0 - Root-Master")

			# Add other Masters as Instances
			for j in range(1, Master_Count, 1):  # 0, Master_Count-1, 1)
				interpol_array.append(Instance_reset_Values[
									  :])  # use as a copy
				interpol_array[-1][j - 1] = 1.0
				# j+1) #Master name (1, 2, ...)
				interpol_array[-1].append(Masters[j].name)
				interpol_array[-1].append(General_Custom_Parameter_Before)

		# -------------------------------------------------
		# -------------------------------------------------

		def process(interpol_array):  # slider,

			# print sliderPos
			# print interpol_array

			interpol_array = []
			InstancesNames = []
			Instances_Count = len(Instances)

			sinnlosboldvalue = []
			sinnlosboldvalue_str = ""
			interpolcalcvalue_new = [0.0, 0.0]
			interpolcalcvalue = [0.0, 0.0]

			# Interpolation Settings (Change Values as needed)
			# -------------------------------------------------

			MasterNamesCalcOrderArray = getInstanceMasterValuesCalcOrder(
				data)  # format is: {"Name of Master":1}
			print "	- MasterNames", MasterNamesCalcOrderArray

			# -------------------------------------------------
			# -------------------------------------------------

			# Excecute / dont't touch if you don't understand ...
			# -------------------------

			# minus "_info" #len(interpol_array)
			Interpol_Count = len(data["InstancesSetup"]) - 1

			print "	-", Interpol_Count, "Setups for Interpolation (", Instances_Count, " current Instances )"
			print " "

			# Add Instances if needed

			if(Instances_reset_all):

				# 1 Delete all Instances
				Font.instances = ()

				# ToDo
				# 2 Add all instances
				#AddInstance(name, filter)

				Instances_added = ""
				for instancename in data["InstancesSetup"]:
					if not instancename.startswith("_"):
						# General_Custom_Parameter_Before_Interpolated_Instances)
						# #Instances_Count + k
						AddInstance(instancename, General_Custom_Parameter_Before)
						Instances_added += instancename + ", "
				print ""
				print ">> Instances removed and added: "
				print ""
				print Instances_added
				print "----------------------------------------------------------------------\n"

			else:
				if(Instances_Count != Interpol_Count):
					raise Exception(
						'Check Instances in the info panel (Names and Count) or activate "Instances_reset_all" in the Multipolation Spec File')

			multiplemode = 1

			# if multiplemode:

			finaloverallcalcsum = [0.0, 0.0]
			interpolmapvalue = [0.0, 0.0]
			interpol_child_sum = [0.0, 0.0]
			interpol_child_calc = [0.0, 0.0]
			interpolcalcvalue = [0.0, 0.0]

			# INSTANCES

			for instancename in data["InstancesSetup"]:

				if not instancename.startswith("_"):

					for charGroupName in data["InstancesSetup"][instancename]:
						if not charGroupName.startswith("_"):
							# print ""
							# print instancename
							# print "----------------------------------------------------------------------"
							# Get Instance (call instance by name would be
							# nicer though!)
							instanceindex = getGSObjectIndex(
								Instances, instancename)
							Instance = Font.instances[instanceindex]
							# print "Instance:", Instance

							Instance.setManualInterpolation_(True)
							# apply master values

							# ignore comments and other data in json
							if not instancename.startswith("_"):

								InstanceName = instancename  # Todo clean up

								finaloverallcalcsum = [0.0, 0.0]
								interpol_sum = [0.0, 0.0]  # clear to zero

								# Iterate through master values to demap the values
								#
								Instance_Custom_Parameter = [] #reset, otherwise all following instances would get the same
								for mastername in data["InstancesSetup"][instancename][charGroupName]:
									if mastername.startswith("_"):
										if mastername.startswith("_Custom_Parameter"):
											Instance_Custom_Parameter = data["InstancesSetup"][instancename][charGroupName][mastername]
										if mastername.startswith("_Active"):
											if data["InstancesSetup"][instancename]["#All"][mastername] == False:
												Instance.active = False



									if not mastername.startswith("_"):
										#"convert mapped values to raw interpolation values"

										# if (XY_Interpolation):
										value_original_readable = [0.0, 0.0]
										interpolmapvalue_new = [0.0, 0.0]

										# BUGFIX-HACK some how sometimes a
										# dictionary comes instead of a list -
										# I really dont know why :/
										test = data["InstancesSetup"][
											instancename][charGroupName][mastername]
										if (type(test) == dict):
											data["InstancesSetup"][instancename][charGroupName][mastername] = data[
												"InstancesSetup"][instancename][charGroupName][mastername]["read"]

										for k in range(len(data["InstancesSetup"][instancename][charGroupName][mastername])):

											value_original_readable[k] = data["InstancesSetup"][
												instancename][charGroupName][mastername][k]
											masterMin = data["MasterSetupMapping"][
												mastername][k][0]
											masterMax = data["MasterSetupMapping"][
												mastername][k][1]

											# print value_original_readable[k], "value_original_readable[k]"
											# print masterMin, "masterMin"
											# print masterMax, "masterMax"
											# print ""

											interpolmapvalue_new[k] = map(value_original_readable[
																		  k], masterMin, masterMax, 0, 1)
											#interpolmapvalue[k] = map(value_original_readable[k], masterMin, masterMax, 0, 1)

											interpol_sum[
												k] += interpolmapvalue_new[k]
										# assign raw value for interpolation
										#
										#

										readablevalue = value_original_readable

										# print mastername, "interpolmapvalue",
										# interpolmapvalue

										data["InstancesSetup"][instancename][charGroupName].update(
											{mastername: {"read": value_original_readable, "map": interpolmapvalue_new, "calc": [0, 0], "childsum": [0, 0]}})

										#[mastername] = {"read","map","calc"}
										# print
										# data["InstancesSetup"][instancename][charGroupName][mastername]

										#Filter = General_Custom_Parameter_Before_Interpolated_Instances

										#interpol_array.append([Master_1, Master_2, Master_3, Master_4, Master_5, InstanceName, Filter])

							# Instance Parent/Child Calculation
							#------------------------------------------
							Instance.setManualInterpolation_(True)
							# print "	calc [x,y]	 read [x,y]
							# min-max [x,y]"
							LocalGlyphInterpolations[0] = ""
							# data["MasterSetupMapping"]:
							# #MasterNamesCalcOrderArray
							for mastername in MasterNamesCalcOrderArray:
								# print "children Calculation / Master:",
								# mastername

								if not mastername.startswith("_"):

									# print "_4__",
									# data["InstancesSetup"][instancename][charGroupName]["Bold"]["calc"]

									interpolmapvalue = data["InstancesSetup"][instancename][charGroupName][mastername]["map"]

									# print mastername

									# check if children

									if (len(data["MasterSetupMapping"][mastername]) > 2):
										# print "yes"
										# if not
										# (type(data["MasterSetupMapping"][mastername][-1])
										# == int):

										#(len(data["MasterSetupMapping"][mastername])>2):

										children = data["MasterSetupMapping"][
											mastername][-1]

										# special "All" case -> add all childs
										if (children == "All"):
											# print "ALL"
											# excludes this mastername
											children = getMasterNames(
												mastername)
											#data["MasterSetupMapping"][mastername]["children"] = children
											data["MasterSetupMapping"][
												mastername][-1] = children

											# Set Order of calculations
											# Root Exception "all" needs to be
											# excecuted last

										masterNameArray = getMasterNames("")
										masterselection = children

										# print "SSSSSSum excecu"

										# print "
										# 31__",
										# data["InstancesSetup"][instancename][charGroupName]["Bold"]["calc"]

										interpol_child_sum = sumSelDictValues(data["InstancesSetup"][instancename][
																			  charGroupName], masterselection, "calc")

										data["InstancesSetup"][instancename][charGroupName][
											mastername]["childsum"] = redefinelist(interpol_child_sum)

										# print "interpol_child_sum",
										# interpol_child_sum

										for k in range(len(interpolcalcvalue)):
											interpolcalcvalue_new[k] = interpolmapvalue[
												k] - interpol_child_sum[k]

										# print "interpolcalcvalue_new",
										# interpolcalcvalue_new

									else:
										for k in range(len(interpolcalcvalue)):
											interpolcalcvalue_new[
												k] = interpolmapvalue[k]

										children = False

									# if (mastername == "Bold"):
									# 	sinnlosboldvalue_str = str(interpolcalcvalue_new)
									# sinnlosboldvalue =
									# redefinelist(interpolcalcvalue_new)#string_to_list(sinnlosboldvalue_str)

									data["InstancesSetup"][instancename][
										charGroupName][mastername]["calc"] = ""

									data["InstancesSetup"][instancename][charGroupName][
										mastername]["calc"] = redefinelist(interpolcalcvalue_new)
									#data["InstancesSetup"][instancename][charGroupName][mastername].update({"calc": interpolcalcvalue_new})

									shit = data["InstancesSetup"][instancename][
										charGroupName][mastername]["calc"]

									# print "___"
									# print "											32__", data["InstancesSetup"][instancename][charGroupName]["Bold"]["calc"]
									# print "___", data["InstancesSetup"][instancename][charGroupName]["Bold"]["calc"]
									# print ""

									interpolcalcvalue = interpolcalcvalue_new
									interpol_child_sum = data["InstancesSetup"][
										instancename][charGroupName][mastername]["childsum"]

									readablevalue = data["InstancesSetup"][
										instancename][charGroupName][mastername]["read"]
									readablevaluespan = [data["MasterSetupMapping"][mastername][
										0], data["MasterSetupMapping"][mastername][1]]

									# print "calc \t read \t span"
									# print "   ", ""+str(interpolcalcvalue)+"", "	 ", readablevalue, "	  ", readablevaluespan, "	   ", mastername
									# Masters[masterindex].id,

									# print "
									# 34__",
									# data["InstancesSetup"][instancename][charGroupName]["Bold"]["calc"]

									# if (children):
									# print "								  ", "childs"
									# print "								  ", children
									# print "
									# [", interpolmapvalue, "-",
									# data["InstancesSetup"][instancename][charGroupName][mastername]["childsum"],
									# "//map - sum value]"

									for k in range(len(finaloverallcalcsum)):
										finaloverallcalcsum[
											k] += interpolcalcvalue[k]

									# print "  =", finaloverallcalcsum
									# print ""

									# Apply General Values
									masterindex = getGSObjectIndex(
										Masters, mastername)

									if (charGroupName == "#All"):
										interpolcalcvalue_x = interpolcalcvalue[
											0]
										interpolcalcvalue_y = interpolcalcvalue[
											1]
										xy_interpolation = NSValue.valueWithPoint_(
											(interpolcalcvalue_x, interpolcalcvalue_y))

										Instance.instanceInterpolations[
											Masters[masterindex].id] = xy_interpolation

									# print "
									# 35__",
									# data["InstancesSetup"][instancename][charGroupName]["Bold"]["calc"]

							# print "_6__", mastername, "Bold", "is",
							# data["InstancesSetup"][instancename][charGroupName]["Bold"]["calc"],
							# "should be", sinnlosboldvalue,
							# sinnlosboldvalue_str

							# Local Glyph Interpolation

							if not (charGroupName == "#All"):
								for k in range(len(Font.masters)):
									mastername = byteify(Font.masters[k].name)

									# for charGroupName in
									# data["InstancesSetup"][instancename][charGroupName][mastername]["calc"]

									interpolcalcvaluesStr = str(data["InstancesSetup"][instancename][charGroupName][
																mastername]["calc"]).replace("[", "{").replace("]", "}")

									#interpolcalcvaluesStr = str(Instance.instanceInterpolations[Masters[k].id]).replace("NSPoint: ", "").replace(" ", "")
									#temp_str = str(interpolcalcvalue_x) + "," + str(interpolcalcvalue_y) + "};{"
									# print interpolcalcvaluesStr
									# print Masters[k].id, ": ",
									# interpolcalcvaluesStr
									LocalGlyphInterpolations[0] += interpolcalcvaluesStr + ";"

									# print "ID"
									# print Masters[masterindex].id
									# print LocalGlyphInterpolations[0]
									# print Instance.instanceInterpolations[Masters[masterindex].id]
									# print
									# print ""


								scope = str(data["InstancesSetup"][instancename][charGroupName]["_Scope"])  # "include:H"
								LocalGlyphInterpolations[0] = "Local Interpolation::=;" + LocalGlyphInterpolations[0] + scope

								# Add Local Interpolation
								AddCustomParameter(Instance, LocalGlyphInterpolations)
							# print "First Master " + Masters[0].id;
							# print "Last Master " + Masters[-1].id;

							# print LocalGlyphInterpolations[0]

					# Add Custom Parameters
					try:
						if Instance_Custom_Parameter:
							AddCustomParameter(Instance, Instance_Custom_Parameter)
					except:
						pass


					# Add General Custom Parameter to All Instances, after
					AddCustomParameter(Instance, General_Custom_Parameter_After)

					if ([1.0, 1.0] == finaloverallcalcsum):
						print "- Instance successful created: ", InstanceName

					# Check if it worked

					# pprint(Instance.instanceInterpolations)
					# print "\n\n\n---------------------\n" + LocalGlyphInterpolations[0]
					# print print "First Master " + Masters[0].id;

		process(interpol_array)


Multipolation()


# Minify
# manually!
	#be aware of  [#All]

# All that does not work: :/
# pyminifier --obfuscate --pyz=Multipolation.pyz Multipolation.py
# pyminifier --pyz=Multipolation.pyz Multipolation.py
# pyminifier --obfuscate -o=Multipolation_min.py Multipolation.py
