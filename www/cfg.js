//
// configuration panel JS handling, all done in vanilla js to keep it easier.
//
var timezones = [
    { value: -12*3600,  label: "UTC-12:00" },
    { value: -11*3600,  label: "UTC-11:00" },
    { value: -10*3600,  label: "UTC-10:00" },
    { value: -9.5*3600, label: "UTC-9:30"  },
    { value: -9*3600,   label: "UTC-9:00"  },
    { value: -8*3600,   label: "UTC-8:00"  },
    { value: -7*3600,   label: "UTC-7:00"  },
    { value: -6*3600,   label: "UTC-6:00"  },
    { value: -5*3600,   label: "UTC-5:00"  },
    { value: -4*3600,   label: "UTC-4:00"  },
    { value: -3*3600,   label: "UTC-3:30"  },
    { value: -3*3600,   label: "UTC-3:00"  },
    { value: -2*3600,   label: "UTC-2:00"  },
    { value: -1*3600,   label: "UTC-1:00"  },
    { value: 0,         label: "UTC"       },
    { value: 1    * 3600,  label: "UTC+01:00" },
    { value: 2    * 3600,  label: "UTC+02:00" },
    { value: 3    * 3600,  label: "UTC+03:00" },
    { value: 3.5  * 3600,  label: "UTC+03:30" },
    { value: 4    * 3600,  label: "UTC+04:00" },
    { value: 5    * 3600,  label: "UTC+05:00" },
    { value: 5.5  * 3600,  label: "UTC+05:30" },
    { value: 5.75 * 3600,  label: "UTC+05:45" },
    { value: 6    * 3600,  label: "UTC+06:00" },
    { value: 6.5  * 3600,  label: "UTC+06:30" },
    { value: 7    * 3600,  label: "UTC+07:00" },
    { value: 8    * 3600,  label: "UTC+08:00" },
    { value: 8.75 * 3600,  label: "UTC+08:45" },
    { value: 9    * 3600,  label: "UTC+09:00" },
    { value: 9.5  * 3600,  label: "UTC+09:30" },
    { value: 10   * 3600,  label: "UTC+10:00" },
    { value: 10.5 * 3600,  label: "UTC+10:30" },
    { value: 11   * 3600,  label: "UTC+11:00" },
    { value: 12   * 3600,  label: "UTC+12:00" },
    { value: 12.75 * 3600,  label: "UTC+12:45" },
    { value: 13   * 3600,  label: "UTC+13:00" },
    { value: 14   * 3600,  label: "UTC+14:00" }
];

function initTimeZones() {
    let utcoffsetSelector = document.getElementById("utcoffset");
    for (var tz in timezones) {
        let opt = document.createElement("option");
        opt.text = timezones[tz].label;
        opt.value = timezones[tz].value;
        utcoffsetSelector.add(opt);
    } 
}

//
// from https://www.cisco.com/assets/sol/sb/WAP321_Emulators/WAP321_Emulator_v1.0.0.3/help/Wireless05.html:
// - string length must be 2-32 characters
// - allowable characters are: ASCII 0x20, 0x21, 0x23, 0x25 through 0x2A, 0x2C through 0x3E, 0x40 through 0x5A, 0x5E through 0x7E. 
// - trailing and leading spaces are not permitted
// - string cannot start with 0x21, 0x23, 0x3B
//
function validateAccessPointName(apname) {
    if (!(2 <= apname.length && apname.length <= 32)) {
        return false;
    }
    
    if ( [ 0x21, 0x23, 0x3B, 0x20 ].includes(apname.charCodeAt(0)) ) {
        return false;
    }

    for (var i = 0; i < apname.length; i++) {
        let ch = apname.charCodeAt(i);
        if ( !(
              ch == 0x20 ||
              ch == 0x21 ||
              ch == 0x23 ||
              (0x25 <= ch && ch <= 0x2A) ||
              (0x2C <= ch && ch <= 0x3E) ||
              (0x40 <= ch && ch <= 0x5A) ||
              (0x5E <= ch && ch <= 0x7E)
            )
        ) {
            return false;
        }
    }

    // catch trailing space (shouldn't get out of bounds error, length was already checkeds)
    return apname.charCodeAt(apname.length - 1) != 0x20;
}

function validateForm() {
    if (!validateAccessPointName(document.getElementById("ap_name").value)) {
        return false;
    }

    return true;
}

function changeDstSelection(which) {
    document.getElementById("dst_off").className = "butane";
    document.getElementById("dst_on").className = "butane";
    document.getElementById("dst_disable").className = "butane";

    document.getElementById(which).className = "butaneselectad";
}

function selectDstOff() {
    changeDstSelection("dst_off");
}

function selectDstOn() {
    changeDstSelection("dst_on");
}

function selectDstDisabled() {
    changeDstSelection("dst_disable");
}

function submitForm() {
    let restreq = {
        'wifi_ap_name':     document.getElementById("ap_name").value,
        'wifi_ap_password': document.getElementById("ap_password").value,
        'utc_offset_seconds': document.getElementById("utcoffset").value,
        'dst_active': document.getElementById("dst_on").className === "butaneselectad",
        'dst_disable': document.getElementById("dst_disable").className === "butaneselectad"
    };

    fetch("/rest/settings",{
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(restreq)
    }).then( (response) => response.json() )
    .then( (response) => {
        document.getElementById("success").style.display = "";
        document.getElementById("form").remove();
        
        // scroll to top of page (needed on mobile)
        document.body.scrollTop = document.documentElement.scrollTop = 0;
    })
    .catch( (error) => {
        console.log(error);
    });
}

function populateSettings() {
    fetch("/rest/settings")
        .then( (response) => response.json() )
        .then( (json) =>  {
            document.getElementById("ap_name").value = json['wifi_ap_name'];
            document.getElementById("utcoffset").value = json['utc_offset_seconds'];

            if (json['dst_disable'] === true) {
                selectDstDisabled();
            } else if (json['dst_active'] === true) {
                selectDstOn();
            } else {
                selectDstOff();
            }
        });
}

document.addEventListener("DOMContentLoaded", function() {
    populateSettings();

    var apname = document.getElementById("ap_name");
    apname.addEventListener('change', function(e) {
        this.setCustomValidity('');
        if (!this.checkValidity()) {
            return;
        }

        if (!validateAccessPointName(apname.value)) {
            this.setCustomValidity('Invalid SSID format');
        }
    });

    document.getElementById("form").style.visibility = "visible";
    initTimeZones();
});