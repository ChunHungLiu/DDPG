#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: Olivier Sigaud

Module: StateEstimator

Description: Used to estimate the current state, reproducing the human control motor delay.
'''
import numpy as np
import random as rd
from gym.envs.motor_control.ArmModel.Arm import get_dotQ_and_Q_From

def isNull(vec):
    for el in vec:
        if el!=0:
            return False
    return True

class State_Estimator:
    
    def __init__(self, dimState, dimCommand, delay, arm):
        '''
    	Initializes parameters to uses the function implemented below
    	
    	inputs:		-dimCommand: dimension of the muscular activation vector U, int (here, 6)
    			-delay: delay in time steps with which we give the observation to the filter, int
    			-arm, armModel, class object
    	'''
        self.name = "StateEstimator"
        self.dimState = dimState
        self.dimCommand = dimCommand
        self.delay = delay
        self.arm = arm

    def init_store(self, state):
        '''
    	Initialization of the observation storage
    
    	Input:		-state: the state stored
    	'''
        self.stateStore = np.zeros((self.delay,self.dimState))
        self.commandStore = np.zeros((self.delay,self.dimCommand))
        #print ("InitStore:", self.stateStore)
        self.currentEstimState = state
        return self.currentEstimState
    
    def store_info(self, state, command):
        '''
    	Stores the current state and returns the delayed state
    
    	Input:		-state: the state to store
    	'''

        self.stateStore[1:]=self.stateStore[:-1]
        self.commandStore[1:]=self.commandStore[:-1]        
        self.stateStore[0]=state
        self.commandStore[0]=command
        #print ("After store:", self.stateStore)
        #print ("retour:", self.stateStore[self.delay-1])
        return self.stateStore[self.delay-1]
    
    def get_estim_state(self, state, command):
        '''
    	Function used to compute the next state approximation with the filter
    
    	Inputs:		-state: the state to feed the filter, numpy array of dimension (x, 1), here x = 4
                        -command: the noiseless muscular activation vector U, numpy array of dimension (x, 1), here x = 6
    
    	Output:		-stateApprox: the next state approximation, numpy array of dimension (x, 1), here x = 4
    	'''
        #store the state of the arm to feed the filter with a delay on the observation
        inferredState = self.store_info(state, command)
        if isNull(inferredState):
            self.currentEstimState = self.arm.computeNextState(command,self.currentEstimState)
            return self.currentEstimState
        newEstimState = self.arm.computeNextState(command,self.currentEstimState)
        for i in range (self.delay):
            U = self.commandStore[self.delay-i-1]
            inferredState = self.arm.computeNextState(U,inferredState)

        for i in range(4):
            self.currentEstimState[i] = (newEstimState[i] + 0.2 * inferredState[i])/1.2
        return self.currentEstimState
    
