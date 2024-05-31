# Copyright (c) 2024, erpdata and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import zk
from datetime import datetime, timedelta
import re  


class BiometricAttendanceSync(Document):
	@frappe.whitelist()
	def check_dates(self):
		if(self.to_date and self.from_date):
			if(self.to_date < self.from_date):
				frappe.throw("From Date can not greater than To Date")
    
	@frappe.whitelist()
	def get_current_date(self):
		self.from_date=datetime.today()
		self.to_date=datetime.today()
	
	@frappe.whitelist()
	def sync_data(self):
		# dict={
			# first shift 3107
			# '2024-03-21-3107': ['3107','2024-03-21 04:08:00','2024-03-21 12:02:00'],
			# '2024-03-21-757': ['757','2024-03-21 04:08:00','2024-03-21 7:02:00'],
			# '2024-03-22-3107': ['3107','2024-03-22 04:02:00'],
			# '2024-03-22-757': ['757','2024-03-22 04:02:00'],
			# '2024-03-23-3107': ['3107','2024-03-23 03:07:00', '2024-03-23 11:03:00'],
			# '2024-03-23-757': ['757','2024-03-23 12:03:00', '2024-03-23 12:07:00'],
			# '2024-03-24-3107': ['3107','2024-03-24 04:08:00', '2024-03-24 04:10:00','2024-03-24 12:04:00'],
			# '2024-03-24-757': ['757','2024-03-24 04:03:00', '2024-03-24 04:07:00','2024-03-24 04:09:00'],
			# '2024-03-25-3107': ['3107','2024-03-25 12:03:00'],
			
			# first shift 757
			# '2024-03-21-757': ['757','2024-03-21 12:02:00'],
			# '2024-03-22-757': ['757','2024-03-22 11:06:00'],
			# '2024-03-23-757': ['757','2024-03-23 04:07:00', '2024-03-23 12:03:00'],
			# '2024-03-24-757': ['757','2024-03-24 04:08:00', '2024-03-24 04:10:00','2024-03-24 12:04:00'],
			# '2024-03-25-757': ['757','2024-03-25 04:09:00'],
			# '2024-03-27-757': ['757','2024-03-27 04:09:00'],
			# '2024-03-21-3127': ['3127','2024-03-21 11:48:00', '2024-03-21 19:45:00'],
			# '2024-03-21-591': ['591','2024-03-21 20:09:00'],

			# second shift
			# '2024-03-21-591': ['591','2024-03-21 12:02:00'],
			# # '2024-03-21-201': ['201','2024-03-21 12:08:00'] ,
			# '2024-03-22-591': ['591','2024-03-22 12:00:00','2024-03-22 12:02:00','2024-03-22 12:10:00'],
			# '2024-03-23-591': ['591','2024-03-23 20:04:00'],
			# '2024-03-24-591': ['591','2024-03-24 20:04:00','2024-03-24 20:10:00'],
			# '2024-03-25-591': ['591','2024-03-25 12:02:00','2024-03-25 12:04:00','2024-03-25 12:10:00','2024-03-25 20:04:00','2024-03-25 20:06:00','2024-03-25 20:10:00',],
			# '2024-03-24-591': ['591','2024-03-24 04:00:00'],        
			# '2024-03-19-3107': ['3107','2024-03-19 00:03:00','2024-03-19 08:01:00'], 

			# third shift
			# '2024-03-21-3007': ['3007','2024-03-21 19:50:00'],
			# '2024-03-22-3007': ['3007','2024-03-22 03:59:00'],
			# '2024-03-23-3007': ['3007','2024-03-23 04:10:00','2024-03-23 04:11:00','2024-03-23 20:05:00','2024-03-23 20:07:00'],
			# '2024-03-25-3007': ['3007','2024-03-25 19:20:00','2024-03-25 20:00:00'],
			# '2024-03-26-3007': ['3007','2024-03-26 03:50:00','2024-03-26 03:59:00','2024-03-26 20:01:00'],
			# '2024-03-27-3007': ['3007','2024-03-27 04:05:00','2024-03-27 04:09:00','2024-03-27 20:05:00','2024-03-27 20:10:00'],
			# '2024-03-23-591': ['591','2024-03-23 20:04:00'],
			# '2024-03-24-591': ['591','2024-03-24 04:01:00','2024-03-24 04:05:00','2024-03-24 04:08:00','2024-03-24 20:02:00'],
			# '2024-03-25-591': ['591','2024-03-25 04:02:00'],
			# '2024-03-18-3107': ['3107','2024-03-19 07:59:00'], ,'2024-03-19 16:10:00',,  '2024-03-19 16:10:00'
		# }
		if(not self.from_date or not self.to_date):
			frappe.throw("Please select from date and to date")
		self.check_dates()
		for j in self.get("machine_configuration"):
			if(j.check):
				dict=self.get_attendance_data(self.from_date,self.to_date,j.machine_ip,j.com_key,j.port_no,j.machine_code)
				# frappe.throw("hiii")
				for i in dict:
					tdate=dict[i][1]
					date_only = datetime.strptime(tdate, '%Y-%m-%d %H:%M:%S').date()
					req_date = date_only.strftime('%Y-%m-%d')
					if(dict[i]!='0'):
						employee_data=frappe.get_value("Employee",{"attendance_device_id":str(dict[i][0]),"status":"Active"},"name")
						emp_id=employee_data
						shift_name= frappe.get_value("Shift Assignment",{'employee':emp_id,"docstatus":1,'start_date':["<=", req_date] , 'end_date': [">=", req_date]},"shift_type")
						if(shift_name and emp_id):
							in_time = None
							out_time = None
							shift=None
							shift_details=frappe.get_value("Shift Type",{"name":shift_name},["start_time","end_time","begin_check_in_before_shift_start_time","allow_check_out_after_shift_end_time","custom_next_day","custom_shift_type"])
							start_time,end_time,begin_check_in_before_shift,allow_check_out_after_shift,next_day,custom_shift_type=shift_details
							next_day = next_day
							custom_shift_type = custom_shift_type
							start_time = datetime.strptime(str(start_time), "%H:%M:%S")		
							end_time = datetime.strptime(str(end_time), "%H:%M:%S")
							
							begin_check_in_before_shift = begin_check_in_before_shift
							allow_check_out_after_shift = allow_check_out_after_shift
							begin_check_in_before_shift_timedelta = timedelta(minutes=begin_check_in_before_shift)
							allow_check_out_after_shift_timedelta = timedelta(minutes=allow_check_out_after_shift)

							# Subtract begin_check_in_before_shift from start_time
							from_date = start_time - begin_check_in_before_shift_timedelta
							# Add allow_check_out_after_shift to end_time
							to_date = end_time + allow_check_out_after_shift_timedelta
							to_date_checkin = end_time - allow_check_out_after_shift_timedelta - begin_check_in_before_shift_timedelta
							
							shift_in_time = from_date.time()
							shift_out_time = to_date.time()
							time_to_checkin = to_date_checkin.time()
						
							check_time1 = datetime.strptime("23:59:59", '%H:%M:%S').time()
							check_time2 = datetime.strptime("18:00:00", '%H:%M:%S').time()
							check_time3 = datetime.strptime("01:00:00", '%H:%M:%S').time()
							check_time4 = datetime.strptime("05:00:00", '%H:%M:%S').time()

							if custom_shift_type == "Third":
								if len(dict[i]) ==2:
									time = dict[i][1]
									datetime_obj=datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S')
									time_part=datetime_obj.strftime('%H:%M:%S')
									time_part=datetime.strptime(time_part, '%H:%M:%S').time()
									if (time_part <= time_to_checkin):
										in_time = dict[i][1]
									else:
										out_time = dict[i][1]
								else:
									out_time = dict[i][-1]
									in_time = dict[i][1]
									out_time=self.check_diff(in_time,out_time)
									if not out_time:									
										time = dict[i][1]
										datetime_obj=datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S')
										time_part=datetime_obj.strftime('%H:%M:%S')
										time_part=datetime.strptime(time_part, '%H:%M:%S').time()
										if(time_part < time_to_checkin):
											in_time =dict[i][1]
											out_time =None
										else:
											out_time=dict[i][-1]
											in_time = None
									
									
							elif custom_shift_type == "Second" :
								if len(dict[i]) ==2:
									time = dict[i][1]
									datetime_obj=datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S')
									time_part=datetime_obj.strftime('%H:%M:%S')
									time_part=datetime.strptime(time_part, '%H:%M:%S').time()
									if (time_part <= time_to_checkin):
										in_time = dict[i][1]
									else:
										out_time = dict[i][1]
								else:
									in_time = dict[i][1]			
									out_time = dict[i][-1]
									out_time=self.check_diff(in_time,out_time)
									if not out_time:									
										time = dict[i][1]
										datetime_obj=datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S')
										time_part=datetime_obj.strftime('%H:%M:%S')
										time_part=datetime.strptime(time_part, '%H:%M:%S').time()
										if(time_part < time_to_checkin):
											in_time =dict[i][1]
											out_time =None
										else:
											out_time=dict[i][-1]
											in_time = None
						
							
							elif custom_shift_type == "Fourth":
								if len(dict[i]) ==2:
									time = dict[i][1]
									datetime_obj=datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S')
									time_part=datetime_obj.strftime('%H:%M:%S')
									time_part=datetime.strptime(time_part, '%H:%M:%S').time()
									if (shift_in_time < time_part < check_time1):
										in_time = dict[i][1]
									else:
										out_time = dict[i][1]
								else:						
									min_diff = float('inf')  # Initialize the minimum difference
									min_diff_in = float('inf')
									for ts in dict[i][1:]:
										ts_obj = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
										ts_time = ts_obj.time()
										
										# Calculate the time difference to 5 AM
										time_diff = abs((ts_time.hour - shift_out_time.hour) * 3600 + (ts_time.minute - shift_out_time.minute) * 60)
										# Calculate the time difference to 8 PM
										time_diff_in = abs((ts_time.hour - shift_in_time.hour) * 3600 + (ts_time.minute - shift_in_time.minute) * 60)
        
										# Update out_time if the difference is smaller
										if time_diff < min_diff:
											min_diff = time_diff
											out_time = ts_obj

										if time_diff_in < min_diff_in:
											min_diff_in = time_diff_in
											in_time = ts_obj

										
									if out_time:
										out_time = out_time.strftime('%Y-%m-%d %H:%M:%S')
									if in_time:
										in_time = in_time.strftime('%Y-%m-%d %H:%M:%S')
									
         		
						
							else:		
								custom_shift_type =="First"
								if len(dict[i]) == 2:
									time = dict[i][1]
									datetime_obj=datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S')
									time_part=datetime_obj.strftime('%H:%M:%S')
									time_part=datetime.strptime(time_part, '%H:%M:%S').time()
									if (time_part <= time_to_checkin):
										in_time = dict[i][1]
									else:
										out_time = dict[i][1]
							
								else:
									in_time = dict[i][1]
									out_time = dict[i][-1]
									out_time=self.check_diff(in_time,out_time)
									if not out_time:									
										time = dict[i][1]
										datetime_obj=datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S')
										time_part=datetime_obj.strftime('%H:%M:%S')
										time_part=datetime.strptime(time_part, '%H:%M:%S').time()
										if(time_part < time_to_checkin):
											in_time =dict[i][1]
											out_time =None
										else:
											out_time=dict[i][-1]
											in_time = None
											
											
								
							
							count=0
							if(custom_shift_type=="First"):
								if(in_time):
									current_date = str(in_time)[:10]
									shift_in_time = current_date + " " + str(shift_in_time)
									shift_in_time = datetime.strptime(shift_in_time, '%Y-%m-%d %H:%M:%S')
									in_time = datetime.strptime(str(in_time), '%Y-%m-%d %H:%M:%S')
								if(out_time):
									current_date = str(out_time)[:10]
									shift_out_time = current_date + " " + str(shift_out_time)
									shift_out_time = datetime.strptime(shift_out_time, '%Y-%m-%d %H:%M:%S')
									out_time = datetime.strptime(str(out_time), '%Y-%m-%d %H:%M:%S')
								
																
							if(custom_shift_type=="Second"):
								if in_time:
									current_date =str(in_time)[:10]		
									shift_in_time = current_date + " " + str(shift_in_time)  # Assuming shift_in_time is a time string
									shift_in_time = datetime.strptime(shift_in_time, '%Y-%m-%d %H:%M:%S')
									in_time = datetime.strptime(str(in_time), '%Y-%m-%d %H:%M:%S')
									

								if out_time:
									current_date = str(out_time)[:10]
									shift_out_time = current_date + " " + str(shift_out_time)
									shift_out_time = datetime.strptime(shift_out_time, '%Y-%m-%d %H:%M:%S')
									out_time = datetime.strptime(str(out_time), '%Y-%m-%d %H:%M:%S')
							
			
							if(custom_shift_type=="Third"):
								if out_time:
									current_date = str(out_time)[:10]
									shift_out_time = current_date + " " + str(shift_out_time)  # Assuming shift_in_time is a time string
									shift_out_time = datetime.strptime(shift_out_time, '%Y-%m-%d %H:%M:%S')
									out_time = datetime.strptime(str(out_time), '%Y-%m-%d %H:%M:%S')
									current_date =str(out_time)[:10]
									date_obj=datetime.strptime(str(current_date), '%Y-%m-%d') + timedelta(days=-1)
									new_date_part=date_obj.strftime('%Y-%m-%d')
									shift_in_time=new_date_part + " " + str(shift_in_time) 
									shift_in_time = datetime.strptime(shift_in_time, '%Y-%m-%d %H:%M:%S')
								
								if in_time:
									in_time = datetime.strptime(str(in_time), '%Y-%m-%d %H:%M:%S')
							
							if(custom_shift_type=="Fourth"):
								if out_time:
									current_date = str(out_time)[:10]
									shift_out_time = current_date + " " + str(shift_out_time)  # Assuming shift_in_time is a time string
									shift_out_time = datetime.strptime(shift_out_time, '%Y-%m-%d %H:%M:%S')
									out_time = datetime.strptime(str(out_time), '%Y-%m-%d %H:%M:%S')
									current_date =str(out_time)[:10]
									date_obj=datetime.strptime(str(current_date), '%Y-%m-%d') + timedelta(days=-1)
									new_date_part=date_obj.strftime('%Y-%m-%d')
									shift_in_time=new_date_part + " " + str(shift_in_time) 
									shift_in_time = datetime.strptime(shift_in_time, '%Y-%m-%d %H:%M:%S')

								if in_time:
									in_time = datetime.strptime(str(in_time), '%Y-%m-%d %H:%M:%S')
								

							shift_out_time = shift_out_time
							shift_in_time = shift_in_time
							
							if(in_time):
								# if(in_time>=shift_in_time and in_time<=shift_out_time):
								count=frappe.db.exists("Employee Checkin", {"employee":emp_id,"time":in_time,"log_type":"IN"})
								if(not count):
									new_doc=frappe.new_doc("Employee Checkin")
									new_doc.employee=emp_id
									new_doc.time=in_time
									new_doc.device_id=j.machine_code
									new_doc.log_type="IN"
									new_doc.save()	

							if(out_time):
								count=frappe.db.exists("Employee Checkin", {"employee":emp_id,"time":out_time,"log_type":"OUT"})
								if(not count):
									new_doc=frappe.new_doc("Employee Checkin")
									new_doc.employee=emp_id
									new_doc.time=out_time
									new_doc.device_id=j.machine_code
									new_doc.log_type="OUT"
									new_doc.save()
							

		
	
	def check_diff(self,in_time,out_time):
		in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
		out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
		diff = out_time - in_time
		if diff <= timedelta(minutes=15):
			out_time = None
		return out_time
 
	def get_attendance_data(self,start_date,end_date,machine_ip,common_key,port,machine_code):    
		zk_instance = zk.base.ZK(machine_ip, port=int(port), timeout=60, password=str(common_key))
		conn=""
		try:
			conn = zk_instance.connect()
			if conn:
				attendance_data = conn.get_attendance()
				conn.disable_device()
				pattern = r"<Attendance>: (\d+) : (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \((\d+), (\d+)\)"
				attendance_records={}
				for record in attendance_data:
					record_date = record.timestamp.date()
					if(record_date.strftime('%Y-%m-%d')>=start_date and record_date.strftime('%Y-%m-%d')<=end_date):   
						attendance_string=record
						match = re.match(pattern,str(attendance_string))
						if match:
							user_id = int(match.group(1))
							timestamp = match.group(2)
							dict_key=f"{record_date.strftime('%Y-%m-%d')}-{user_id}"
							if(dict_key not in attendance_records):
								attendance_records[dict_key]=[str(user_id),timestamp]
							else:
								attendance_records[dict_key].append(timestamp)
				return attendance_records
		except Exception as e:
			frappe.throw(f"There Is Connecting Issue With Machine {machine_code}")
		finally:
			if conn:
				conn.disconnect()