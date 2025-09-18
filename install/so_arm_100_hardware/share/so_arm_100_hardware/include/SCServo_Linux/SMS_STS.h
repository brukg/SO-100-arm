/*
 * SMS_STS.h
 * Feetech SMS/STS Series Serial Servo Application Layer Program Header
 * Date: 2021.12.8
 * Author: 
 */

#ifndef _SMS_STS_H
#define _SMS_STS_H

// Baud rate definition
#define	SMS_STS_1M 0
#define	SMS_STS_0_5M 1
#define	SMS_STS_250K 2
#define	SMS_STS_128K 3
#define	SMS_STS_115200 4
#define	SMS_STS_76800 5
#define	SMS_STS_57600 6
#define	SMS_STS_38400 7

//Memory table definition
//-------EPROM (Read only)--------
#define SMS_STS_MODEL_L 3
#define SMS_STS_MODEL_H 4

//-------EPROM(读写)--------
#define SMS_STS_ID 5
#define SMS_STS_BAUD_RATE 6
#define SMS_STS_MIN_ANGLE_LIMIT_L 9
#define SMS_STS_MIN_ANGLE_LIMIT_H 10
#define SMS_STS_MAX_ANGLE_LIMIT_L 11
#define SMS_STS_MAX_ANGLE_LIMIT_H 12
#define SMS_STS_CW_DEAD 26
#define SMS_STS_CCW_DEAD 27
#define SMS_STS_OFS_L 31
#define SMS_STS_OFS_H 32
#define SMS_STS_MODE 33

//-------SRAM(读写)--------
#define SMS_STS_TORQUE_ENABLE 40
#define SMS_STS_ACC 41
#define SMS_STS_GOAL_POSITION_L 42
#define SMS_STS_GOAL_POSITION_H 43
#define SMS_STS_GOAL_TIME_L 44
#define SMS_STS_GOAL_TIME_H 45
#define SMS_STS_GOAL_SPEED_L 46
#define SMS_STS_GOAL_SPEED_H 47
#define SMS_STS_LOCK 55

//-------SRAM(只读)--------
#define SMS_STS_PRESENT_POSITION_L 56
#define SMS_STS_PRESENT_POSITION_H 57
#define SMS_STS_PRESENT_SPEED_L 58
#define SMS_STS_PRESENT_SPEED_H 59
#define SMS_STS_PRESENT_LOAD_L 60
#define SMS_STS_PRESENT_LOAD_H 61
#define SMS_STS_PRESENT_VOLTAGE 62
#define SMS_STS_PRESENT_TEMPERATURE 63
#define SMS_STS_MOVING 66
#define SMS_STS_PRESENT_CURRENT_L 69
#define SMS_STS_PRESENT_CURRENT_H 70

#include "SCSerial.h"

class SMS_STS : public SCSerial
{
public:
	SMS_STS();
	SMS_STS(u8 End);
	SMS_STS(u8 End, u8 Level);
	virtual int WritePosEx(u8 ID, s16 Position, u16 Speed, u8 ACC = 0); // Mode 0: Ordinary write single servo position
	virtual int RegWritePosEx(u8 ID, s16 Position, u16 Speed, u8 ACC = 0); // Mode 0: Async write single servo position (RegWriteAction takes effect)
	virtual void SyncWritePosEx(u8 ID[], u8 IDN, s16 Position[], u16 Speed[], u8 ACC[]); // Mode 0: Sync write multiple servo positions
	virtual int Mode(u8 ID, u8 mode); // Set mode: 0 (servo), 1 (wheel; closed loop) or 2 (wheel; open loop)
	virtual int WriteSpe(u8 ID, s16 Speed, u8 ACC = 0); // Mode 1: Ordinary write single servo speed
	virtual int RegWriteSpe(u8 ID, s16 Speed, u8 ACC = 0); // Mode 1: Async write single servo speed
	virtual void SyncWriteSpe(u8 ID[], u8 IDN, s16 Speed[], u8 ACC[]); // Mode 1: Sync write multiple servo speeds
	virtual int WritePwm(u8 ID, s16 Pwm); //Mode 2: Ordinary write single servo PWM
	virtual int RegWritePwm(u8 ID, s16 Pwm); //Mode 2: Async write single servo PWM
	virtual void SyncWritePwm(u8 ID[], u8 IDN, s16 Pwm[]); // Mode 2: Sync write multiple servo PWMs
	virtual int EnableTorque(u8 ID, u8 Enable); // Enable torque
	virtual int unLockEprom(u8 ID); // EEPROM unlock 
	virtual int LockEprom(u8 ID);// EEPROM lock
	virtual int CalibrationOfs(u8 ID); // Median calibration
	virtual int FeedBack(int ID); // Servo feedback information 
	virtual int ReadPos(int ID); // Read servo position
	virtual int ReadSpeed(int ID); // Read servo speed
	virtual int ReadLoad(int ID); // Read PWM percentage output to the motor ([-1000, 1000] = [100% reverse, 100% forward])
	virtual int ReadVoltage(int ID); // Read motor voltage 
	virtual int ReadTemper(int ID); // Read motor temperature
	virtual int ReadMove(int ID); // Read motion status
	virtual int ReadCurrent(int ID); // Read motor current
private:
	u8 Mem[SMS_STS_PRESENT_CURRENT_H-SMS_STS_PRESENT_POSITION_L+1];
};

#endif