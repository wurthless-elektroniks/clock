//
// Seven-segment multiplexer for Attiny, for boards with micropython hosts
// that are too slow or don't have enough I/Os (ESP32-C3 comes to mind)
// Target chip is Attiny816
//

#include <Wire.h>
#include <twi.h>
#include <twi_pins.h>

uint8_t cells[4];
uint8_t tick;

#define M_TickToDigit(tick) (tick >> 2)

ISR(TCA0_OVF_vect) {
  // tick is in 4 steps:
  // 0 - latch segments
  // 1 - latch digit drive
  // 2 - nop
  // 3 - clear digit drive
  switch(tick & 3) {
    case 0:
      VPORTA_OUT = cells[M_TickToDigit(tick)];
      break;
    case 1:
      VPORTC_OUT = 1 << M_TickToDigit(tick);
      break;
    case 3:
      VPORTC_OUT = 0;
      break;

    case 2:
    default:
      break;
  }

  tick ++;
  tick &= 0x0F;

  // ack interrupt
  TCA0.SINGLE.INTFLAGS = TCA_SINGLE_OVF_bm;
}

uint8_t poll() {
  while(!Wire.available());
  return Wire.read();
}

void i2cEvent(int numbytes) {
  if (numbytes < 1) {
    return;
  }

  switch(poll()) {
    case 1: // set digits
      {
        // load data from I2C
        for (int i = 0; i < 4; i++) {
          cells[i] = poll() << 1; // shifted left once due to how pins are connected to port A
        }
      }
      break;

    default:
      return;
  }
}

// modified from Microchip example
// https://github.com/MicrochipTech/TB3217_Getting_Started_with_TCA/blob/master/Using_periodic_interrupt_mode/main.c
void TCA0_init(void)
{
    /* enable overflow interrupt */
    TCA0.SINGLE.INTCTRL = TCA_SINGLE_OVF_bm;
    
    /* set Normal mode */
    TCA0.SINGLE.CTRLB = TCA_SINGLE_WGMODE_NORMAL_gc;
    
    /* disable event counting */
    TCA0.SINGLE.EVCTRL &= ~(TCA_SINGLE_CNTEI_bm);
    
    /* set the period */
    // excel formula: =(16000000 / 256) * A2 / 16000000
    TCA0.SINGLE.PER = 15;
    
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV256_gc         /* set clock source (sys_clk/256) */
                      | TCA_SINGLE_ENABLE_bm;                /* start timer */
}


void setup() {
  // join I2C bus as slave
  Wire.begin(0x69, true);
  Wire.onReceive(i2cEvent);

  // "ABCD"
  cells[0] = 0b11101110;
  cells[1] = 0b11111110;
  cells[2] = 0b01110010;
  cells[3] = 0b10111100;
  tick = 0;

  // port A bit 0 is UPDI
  // all others are the seven-segment drives (1 = A, 2 = B... 7 = G)
  VPORTA_DIR = 0b11111110;

  // port C are digit drives
  VPORTC_DIR = 0b00001111;

  // init timer
  TCA0_init();
}

void loop() {
  // everything is IRQ driven
}

