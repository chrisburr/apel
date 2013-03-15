#!/usr/bin/env python

#   Copyright (C) 2012 STFC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
'''
   @author: Will Rogers
'''

import sys
import os
from dirq.queue import Queue
from dirq.QueueSimple import QueueSimple
from apel.db.loader.loader import QSCHEMA
    
    
def check_dir(root):
    '''
    Check the directory for incoming, outgoing, reject
    or accept directories.  If they exist, check them for 
    messages.
    ''' 
    print 'Starting message status script.' 
    print 'Root directory: %s' % root
    queues = []
    incoming = os.path.join(root, 'incoming')
    if os.path.isdir(incoming):
        queues.append(Queue(incoming, schema=QSCHEMA))
    outgoing = os.path.join(root, 'outgoing')
    # outgoing uses QueueSimple, not Queue
    if os.path.isdir(outgoing):
        queues.append(QueueSimple(outgoing))
    reject = os.path.join(root, 'reject')
    if os.path.isdir(reject):
        queues.append(Queue(reject, schema=QSCHEMA))
    accept = os.path.join(root, 'accept')
    if os.path.isdir(accept):
        queues.append(Queue(accept, schema=QSCHEMA))
    
    for q in queues:
        msgs, locked = check_queue(q)
        print '    Messages: %s' % msgs 
        print '    Locked:   %s' % locked
        print 
        if locked > 0:
            question = 'Unlock %s messages?' % locked
            if ask_user(question):
                clear_locks(q)
                
    
def check_queue(q):
    '''
    Given a queue, check through all messages to 
    see if any are locked.  Return <total>, <number locked>.
    '''
    print 'Checking directory: %s' % q.path
    locked = 0
    name = q.first()
    # loop until there are no messages left
    while name:
        if not q.lock(name):
            locked += 1
            #print "Locked message: ID = %s" % name
            name = q.next()
            #q.unlock(name)
            continue
        #print "# reading element %s" % name
        else:
            q.unlock(name)
            name = q.next()
    
    return q.count(), locked
    
    
def clear_locks(q):
    '''
    Go through all messages and remove any locks.
    '''
    name = q.first()
    while name:
        if not q.lock(name):
            q.unlock(name)
            name = q.next()
    
    
def ask_user(question):
    '''
    Ask the user to confirm the specified yes/no question.
    '''
    while True:
        ans = raw_input('%s (y/n) ' % question).lower()
        if ans == 'y':
            return True
        elif ans == 'n':
            return False
        else:
            print 'Choose y or n:'
            continue
        
        
if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print "Usage: %s <path to messages directory>"
        sys.exit()
    
    if not os.path.isdir(sys.argv[1]):
        print 'Directory %s does not exist. Exiting.' % sys.argv[1]
        sys.exit()
        
    check_dir(sys.argv[1])
    
