/*
 * SMSCL.h
 * SMSCLϵ�д��ж���ӿ�
 * ����: 2020.6.17
 * ����: 
 */

#ifndef _SMSCL_H
#define _SMSCL_H


#define	SMSCL_1M 0
#define	SMSCL_0_5M 1
#define	SMSCL_250K 2
#define	SMSCL_128K 3
#define	SMSCL_115200 4
#define	SMSCL_76800	5
#define	SMSCL_57600	6
#define	SMSCL_38400	7

//�ڴ������
//-------EPROM(ֻ��)--------
#define SMSCL_VERSION_L 3
#define SMSCL_VERSION_H 4

//-------EPROM(��д)--------
#define SMSCL_ID 5
#define SMSCL_BAUD_RATE 6
#define SMSCL_RETURN_DELAY_TIME 7
#define SMSCL_RETURN_LEVEL 8
#define SMSCL_MIN_ANGLE_LIMIT_L 9
#define SMSCL_MIN_ANGLE_LIMIT_H 10
#define SMSCL_MAX_ANGLE_LIMIT_L 11
#define SMSCL_MAX_ANGLE_LIMIT_H 12
#define SMSCL_LIMIT_TEMPERATURE 13
#define SMSCL_MAX_LIMIT_VOLTAGE 14
#define SMSCL_MIN_LIMIT_VOLTAGE 15
#define SMSCL_MAX_TORQUE_L 16
#define SMSCL_MAX_TORQUE_H 17
#define SMSCL_ALARM_LED 19
#define SMSCL_ALARM_SHUTDOWN 20
#define SMSCL_COMPLIANCE_P 21
#define SMSCL_COMPLIANCE_D 22
#define SMSCL_COMPLIANCE_I 23
#define SMSCL_PUNCH_L 24
#define SMSCL_PUNCH_H 25
#define SMSCL_CW_DEAD 26
#define SMSCL_CCW_DEAD 27
#define SMSCL_OFS_L 33
#define SMSCL_OFS_H 34
#define SMSCL_MODE 35
#define SMSCL_MAX_CURRENT_L 36
#define SMSCL_MAX_CURRENT_H 37	

//-------SRAM(��д)--------
#define SMSCL_TORQUE_ENABLE 40
#define SMSCL_ACC 41
#define SMSCL_GOAL_POSITION_L 42
#define SMSCL_GOAL_POSITION_H 43
#define SMSCL_GOAL_TIME_L 44
#define SMSCL_GOAL_TIME_H 45
#define SMSCL_GOAL_SPEED_L 46
#define SMSCL_GOAL_SPEED_H 47
#define SMSCL_LOCK 48

//-------SRAM(ֻ��)--------
#define SMSCL_PRESENT_POSITION_L 56
#define SMSCL_PRESENT_POSITION_H 57
#define SMSCL_PRESENT_SPEED_L 58
#define SMSCL_PRESENT_SPEED_H 59
#define SMSCL_PRESENT_LOAD_L 60
#define SMSCL_PRESENT_LOAD_H 61
#define SMSCL_PRESENT_VOLTAGE 62
#define SMSCL_PRESENT_TEMPERATURE 63
#define SMSCL_REGISTERED_INSTRUCTION 64
#define SMSCL_MOVING 66
#define SMSCL_PRESENT_CURRENT_L 69
#define SMSCL_PRESENT_CURRENT_H 70

#include "SCSerial.h"

class SMSCL : public SCSerial
{
public:
	SMSCL();
	SMSCL(u8 End);
	SMSCL(u8 End, u8 Level);
	virtual int WritePosEx(u8 ID, s16 Position, u16 Speed, u8 ACC = 0);//��ͨд�������λ��ָ��
	virtual int RegWritePosEx(u8 ID, s16 Position, u16 Speed, u8 ACC = 0);//�첽д�������λ��ָ��(RegWriteAction��Ч)
	virtual void SyncWritePosEx(u8 ID[], u8 IDN, s16 Position[], u16 Speed[], u8 ACC[]);//ͬ��д������λ��ָ��
	virtual int WheelMode(u8 ID);//����ģʽ
	virtual int WriteSpe(u8 ID, s16 Speed, u8 ACC = 0);//����ģʽ����ָ��
	virtual int EnableTorque(u8 ID, u8 Enable);//Ť������ָ��
	virtual int unLockEprom(u8 ID);//eprom����
	virtual int LockEprom(u8 ID);//eprom����
	virtual int CalibrationOfs(u8 ID);//��λУ׼
	virtual int FeedBack(int ID);//���������Ϣ
	virtual int ReadPos(int ID);//��λ��
	virtual int ReadSpeed(int ID);//���ٶ�
	virtual int ReadLoad(int ID);//�����������ĵ�ѹ�ٷֱ�(0~1000)
	virtual int ReadVoltage(int ID);//����ѹ
	virtual int ReadTemper(int ID);//���¶�
	virtual int ReadMove(int ID);////���ƶ�״̬
	virtual int ReadCurrent(int ID);//������
private:
	u8 Mem[SMSCL_PRESENT_CURRENT_H-SMSCL_PRESENT_POSITION_L+1];
};

#endif