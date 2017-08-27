// ################################################################################
// #                                                                              #
// #                                                                              #
// #           IMPORTANT: READ BEFORE DOWNLOADING, COPYING AND USING.             #
// #                                                                              #
// #                                                                              #
// #      Copyright [2017] [ShenZhen Longer Vision Technology], Licensed under    #
// #      ******** GNU General Public License, version 3.0 (GPL-3.0) ********     #
// #      You are allowed to use this file, modify it, redistribute it, etc.      #
// #      You are NOT allowed to use this file WITHOUT keeping the License.       #
// #                                                                              #
// #      Longer Vision Technology is a startup located in Chinese Silicon Valley #
// #      NanShan, ShenZhen, China, (http://www.longervision.cn), which provides  #
// #      the total solution to the area of Machine Vision & Computer Vision.     #
// #      The founder Mr. Pei JIA has been advocating Open Source Software (OSS)  #
// #      for over 12 years ever since he started his PhD's research in England.  #
// #                                                                              #
// #      Longer Vision Blog is Longer Vision Technology's blog hosted on github  #
// #      (http://longervision.github.io). Besides the published articles, a lot  #
// #      more source code can be found at the organization's source code pool:   #
// #      (https://github.com/LongerVision/OpenCV_Examples).                      #
// #                                                                              #
// #      For those who are interested in our blogs and source code, please do    #
// #      NOT hesitate to comment on our blogs. Whenever you find any issue,      #
// #      please do NOT hesitate to fire an issue on github. We'll try to reply   #
// #      promptly.                                                               #
// #                                                                              #
// #                                                                              #
// # Version:          0.0.1                                                      #
// # Author:           Zhuang Bonan                                               #
// # Contact:          zhuangbonan@longervision.com                               #
// # URL:              http://www.longervision.cn                                 #
// # Create Date:      2017-04-10                                                 #
// ################################################################################

function XmlHttp(){
    var xmlhttp;
    if (window.XMLHttpRequest)
    {
        // code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else
    {
        // code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    sendGET = function(param)
    {
        xmlhttp.open("GET",param,true);
        xmlhttp.send();
    }
    sendPOST = function(path,param)
    {
        xmlhttp.open("POST",path,true);
        xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        xmlhttp.send(param);
    }
    setCbFunc = function(cb)
    {
        xmlhttp.onreadystatechange = cb;
    }
    getResponse = function()
    {
        return {
            readyState:xmlhttp.readyState, 
            status:xmlhttp.status,
            responseText:xmlhttp.responseText,
            responseXML:xmlhttp.responseXML
        };
    }
    return {
        sendGET:sendGET,
        sendPOST:sendPOST,
        setCbFunc:setCbFunc,
        getResponse:getResponse
    };
}

function PinControl()
{
    var pinStates = []
    var http = XmlHttp();
    callback = function()
    {
        var response = http.getResponse();
        if (response.readyState==4 && response.status==200)
        {
            x=response.responseXML.documentElement.getElementsByTagName("Pin");
            //alert(response.responseText);
            id=x[0].getAttribute("id");
            state=x[0].getAttribute("state");
            dir = x[0].getAttribute("dir");
            classes = document.getElementById("pin"+id).className.split(" ");
            i = 0;
            for(;i<classes.length; i++)
            {
                if(classes[i] == 'pinOnOut' || 
                   classes[i] == 'pinOffOut' ||
                   classes[i] == 'pinOnIn' ||
                   classes[i] == 'pinOffIn' ||
                   classes[i] == 'pinBusy')
                   break;
            }
            if (state == "Error")
            {
                alert("Set pin"+id+" error");
            }
            else 
            {
                if(dir == "In")
                {
                    pinStates[id] = -1;
                }
                else 
                {
                    if(state == "On")
                    {
                        pinStates[id] = 1;
                    }
                    else if (state == "Off")
                    {
                        pinStates[id] = 0;
                    }
                }
                classes[i] = 'pin' + state + dir;
                document.getElementById("pin"+id).className = classes.join(" ");
                document.getElementById("pin"+id+"Dir").innerHTML=dir;
            }
            
            //http = null;
        }
    }
    http.setCbFunc(callback);
    changeState = function(id)
    {
        pin = id.split("pin")[1]
        if(pinStates[pin] != -1 && pinStates != -2)
        {
            http.sendPOST("pinChange?pin="+pin);
            pinStates[pin] = -1;
            classes = document.getElementById(id).className.split(" ");
            i = 0;
            for(;i<classes.length; i++)
            {
                if(classes[i] == 'pinOnOut' || 
                   classes[i] == 'pinOffOut' ||
                   classes[i] == 'pinOnIn' ||
                   classes[i] == 'pinOffIn' ||
                   classes[i] == 'pinBusy')
                   break;
            }
            classes[i]="pinBusy";
            document.getElementById(id).className = classes.join(" ");
        }
    }
    changeDir = function(id)
    {
        pin = id.split("pin")[1].split("Dir")[0]
        if(pinStates[pin] != -2)
        {
            http.sendPOST("pinChangeDir?pin="+pin);
            pinStates[pin] = -2;
            classes = document.getElementById(id).className.split(" ");
            i = 0;
            for(;i<classes.length; i++)
            {
                if(classes[i] == 'pinOnOut' || 
                   classes[i] == 'pinOffOut' ||
                   classes[i] == 'pinOnIn' ||
                   classes[i] == 'pinOffIn' ||
                   classes[i] == 'pinBusy')
                   break;
            }
            classes[i]="pinBusy";
            document.getElementById(id).className = classes.join(" ");
        }
    }
    return {
        changeState:changeState,
        changeDir:changeDir
    };
}

function UpdateTime()
{
    var http = XmlHttp();
    var isOn = false;
    updateInfo = function()
    {
        var response = http.getResponse();
        if (response.readyState==4 && response.status==200)
        {
            if(isOn)
            {
                document.getElementById("time").innerHTML=response.responseText;
                
                setTimeout("update()",1000);
            }
        }
    }
    http.setCbFunc(updateInfo);
    update = function(){
        http.sendGET("time");
    }
    startTimer = function()
    {
        isOn = true;
        update();
    }
    stopTimer = function()
    {
        isOn = false;
    }
    return {
        startTimer:startTimer,
        stopTimer:stopTimer
    };
}


function UpdatePinState()
{
    var http = XmlHttp();
    updateInfo = function(){
        var response = http.getResponse();
        if (response.readyState==4 && response.status==200)
        {
            x=response.responseXML.documentElement.getElementsByTagName("Pin");

            txt="<table border='1'><tr><th>Command Lists</th></tr>";
            for (i=0;i<x.length;i++)
            {
                id=x[i].getAttribute("id");
                state=x[i].getAttribute("state");
                dir=x[i].getAttribute("dir");
                cmd=x[i].getAttribute("cmd");
                if(cmd != "")
                {
                    txt=txt + "<tr>";
                    try
                    {
                        txt=txt + "<td>" + cmd + "</td>";
                    }
                    catch (er)
                    {
                        txt=txt + "<td> </td>";
                    }
                    txt=txt + "</tr>";
                }
                classes = document.getElementById("pin"+id).className.split(" ");
                j = 0;
                for(;j<classes.length; j++)
                {
                    if(classes[j] == 'pinOnOut' || 
                       classes[j] == 'pinOffOut' ||
                       classes[j] == 'pinOnIn' ||
                       classes[j] == 'pinOffIn' ||
                       classes[j] == 'pinBusy')
                       break;
                }
                classes[j] = 'pin' + state + dir;

                document.getElementById("pin"+id).className = classes.join(" ");

                document.getElementById("pin"+id+"Dir").innerHTML=dir;
            }
            txt=txt + "</table>";
            document.getElementById("cmdRes").innerHTML=txt;
            setTimeout("update()",10)
        }
    }
    http.setCbFunc(updateInfo);
    update = function(){
        http.sendGET("status");
    }
    return {
        update:update
    };
}

function CmdControl()
{
    var http = XmlHttp();
    callback = function()
    {
        var response = http.getResponse();
        if (response.readyState==4 && response.status==200)
        {
            res = response.responseText;
            if(res != "Success")
                alert(res)
        }
    }
    http.setCbFunc(callback);
    addCmd = function()
    {
        outId = document.getElementById("outInput").value;
        cmd = document.getElementById("cmdInput").value;

        http.sendPOST("sendCmd?"+outId+"="+cmd);
    }
    return {
        addCmd:addCmd
    };
}
