#
# Copyright (c) 2014, md_5. All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import znc
import znc_core
from datetime import datetime
from pymongo import MongoClient
from queue import Queue
from threading import Thread

# To add a user
# db.addUser({user: "znc", pwd:"znc", "roles": ["readWrite"]})
# sudo apt-get install python3-pymongo

class MongoLog(znc.Module):
    # Module Stuff
    description = 'Logs stuff to MongoDB'
    module_types = [znc.CModInfo.GlobalModule, znc.CModInfo.UserModule, znc.CModInfo.NetworkModule]

    def PutLog(self, stuff):
        stuff['log-user'] = self.GetUser().GetUserName()
        stuff['log-network'] = self.GetNetwork().GetName()
        stuff['log-time'] = datetime.utcnow()

        entry = {}
        for key in stuff:
            value = stuff[key]
            if isinstance(value, znc_core.CPyRetString):
                value = str(value)
                print(value)
            entry[key] = value

        try:
            self.mongo.insert(entry)
            self.PutModule('We just logged %s' % entry)
        except Exception as e:
            self.PutModule('Fatal exception %s' % e)

    def OnLoad(self, sArgs, sMessage):
        args = sArgs.split()
        if len(args) != 3:
            raise Exception('Not enough arguments, syntax: <connection string> <database> <collection>')

        self.mongo = MongoClient(args[0])[args[1]][args[2]]

        return True

    def OnShutdown(self):
        # self.queue.join()
        pass

    def OnIRCConnected(self):
        self.PutLog({
            'connect': GetServer()
            })
        return znc.CONTINUE

    def OnIRCDisconnected(self):
        self.PutLog({
            'disconnect': GetServer()
            })
        return znc.CONTINUE

    def OnRawMode(self, OpNick, Channel, sModes, sArgs):
        self.PutLog({
            'user': OpNick.GetNick(),
            'window': Channel.GetName(),
            'modes': sModes,
            'args': sArgs,
            })
        return znc.CONTINUE

    def OnKick(self, OpNick, sKickedNick, Channel, sMessage):
        self.PutLog({
            'user': sKickedNick,
            'window': Channel.GetName(),
            'operator': OpNick.GetNick(),
            'kick-message': sMessage
            })
        return znc.CONTINUE

    def OnQuit(self, Nick, sMessage, vChans):
        for Channel in vChans:
            self.PutLog({
                'user': Nick.GetNick(),
                'ident': Nick.GetIdent(),
                'host': Nick.GetHost(),
                'window': Channel.getName(),
                'quit-message': sMessage
                });
        return znc.CONTINUE

    def OnJoin(self, Nick, Channel):
        self.PutLog({
            'user': Nick.GetNick(),
            'ident': Nick.GetIdent(),
            'host': Nick.GetHost(),
            'window': Channel.GetName()
            })
        return znc.CONTINUE

    def OnPart(self, Nick, Channel, sMessage):
        self.PutLog({
            'user': Nick.GetNick(),
            'ident': Nick.GetIdent(),
            'host': Nick.GetHost(),
            'window': Channel.GetName(),
            'part-message': sMessage
            })
        return znc.CONTINUE
    def OnNick(self, Nick, sNewNick, vChans):
        for Channel in vChans:
            self.PutLog({
                'user': Nick.GetNick(),
                'window': Channel.getName(),
                'nick': sNewNick
                });
        return znc.CONTINUE

    def OnTopic(self, Nick, Channel, sTopic):
        self.PutLog({
            'user': Nick.GetNick(),
            'window': Channel.GetName(),
            'topic': sTopic
            })
        return znc.CONTINUE

    # Notices
    def OnUserNotice(self, sTarget, sMessage):
        self.PutLog({
            'user': self.GetNetwork().GetCurNick(),
            'window': sTarget,
            'notice': sMessage
            })
        return znc.CONTINUE
    def OnPrivNotice(self, Nick, sMessage):
        self.PutLog({
            'user': Nick.GetNick(),
            'window': Nick,
            'notice': sMessage
            })
        return znc.CONTINUE
    def OnChanNotice(self, Nick, Channel, sMessage):
        self.PutLog({
            'user': Nick.GetNick(),
            'window': Channel.GetName(),
            'notice': sMessage
            })
        return znc.CONTINUE

    # Actions
    def OnUserAction(self, sTarget, sMessage):
        self.PutLog({
            'user': self.GetNetwork().GetCurNick(),
            'window': sTarget,
            'action': sMessage
            })
        return znc.CONTINUE
    def OnPrivAction(self, Nick, sMessage):
        self.PutLog({
            'user': Nick.GetNick(),
            'window': Nick.GetNick(),
            'action': sMessage
            })
        return znc.CONTINUE
    def OnChanAction(self, Nick, Channel, sMessage):
        self.PutLog({
            'user': Nick.GetNick(),
            'window': Channel.GetName(),
            'action': sMessage
            })
        return znc.CONTINUE

    # Messages
    def OnUserMsg(self, sTarget, sMessage):
        self.PutLog({
            'user': self.GetNetwork().GetCurNick(),
            'window': sTarget,
            'message': sMessage
            })
        return znc.CONTINUE
    def OnPrivMsg(self, Nick, sMessage):
        self.PutLog({
            'user': Nick.GetNick(),
            'window': Nick.GetNick(),
            'message': sMessage
            })
        return znc.CONTINUE
    def OnChanMsg(self, Nick, Channel, sMessage):
        self.PutLog({
            'user': Nick.GetNick(),
            'window': Channel.GetName(),
            'message': sMessage
            })
        return znc.CONTINUE
