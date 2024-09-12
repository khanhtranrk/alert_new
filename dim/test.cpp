#include<cstdio>
#include<cstdlib>

// 4 bytes | 4 bytes
#define SCRIPT_LEN 8
char *script;
char *phrases;
int script_len;

// Sim var
unsigned char ind = 0;
unsigned char loop = 0;
unsigned char delay = 0; // delay = it * 5 (minute)
unsigned char custom_1_unit = 0; // vol = it * 100
unsigned char custom_2_unit = 0; // vol = it * 200
unsigned char noise_unit = 0; // vol = it * 100

// impact global variables
void extract_script(char *script, int len) {
    if (len < 4) {
        return;
    }

    // extract custom units
    custom_1_unit = *script >> 4;
    custom_2_unit = (custom_1_unit << 4) ^ *script;

    // extract noise index
    noise_unit = *(script + 1) >> 4;
    ind = (noise_unit << 4) ^ *(script + 1);

    // extract delay_unit, loop
    delay = *(script + 2) >> 4;
    loop = (delay << 4) ^ *(script + 2);

    // extract phrases
    // do not free script
    phrases = script + 4;
}

int once = 0;

void refresh_script() {
    if (once != 0) {
        return;
    }

    extract_script(script, script_len);
    once ++;
}

void play_sound(char pac) {
    // with noise
    if (pac == 0b00000010) {
        std::printf("play hig\n");
        return;
        // play hig
    }

    if (pac == 0b00000100) {
        std::printf("play med\n");
        return;
        // play med
    }

    if (pac == 0b00000110) {
        std::printf("play med\n");
        return;
        // play low
    }

    if (pac == 0b00001000) {
        std::printf("play custom 1\n");
        return;
        // play custom 1
    }

    if (pac ^ 0b00001010) {
        std::printf("play custom 2\n");
        return;
        // play custom 2
    }

    if (pac ^ 0b00001100) {
        std::printf("play spec 1\n");
        return;
        // play spec 1
    }

    if (pac ^ 0b00001110) {
        std::printf("play spec 2\n");
        return;
        // play spec 2
    }

    std::printf("play off\n");
    // delay for off
}

// only use 4 last bits
// only 5 minutes for a time
// 4 first bits must be 0
void play(char pac) {
    if (pac & 0b00000001) {
        pac = pac ^ 0b00000001;
        play_sound(pac);

        // play noise
        std::printf("play noise\n");
        return;
    }

    play_sound(pac);

    // delay
    std::printf("delay\n");
}

void _loop() {
    refresh_script();

    if (script_len < 4) {
        std::printf("error alert");
        // error alert
    } else if (script_len == 4) {
        std::printf("off");
        // off
    } else {
        unsigned char sound_pac = *(phrases + ind*2);
        unsigned char frequence_pac = *(phrases + ind*2 + 1);

        std::printf("play on context: index=%d loop=%d delay=%d\n", ind, loop, delay);
        std::printf("base on        : index=%d loop=%d delay=%d\n", (script_len - 4)/2, (((frequence_pac >> 4) << 4)^frequence_pac), (frequence_pac >> 4));

        if (delay == 0) {
            play(sound_pac >> 4);
        } else {
            play((sound_pac << 4) >> 4);
        }

        delay ++;

        if (delay > (frequence_pac >> 4)) {
            delay = 0;
            loop ++;
        }

        if (loop > (((frequence_pac >> 4) << 4)^frequence_pac)) {
            loop = 0;
            ind ++;
        }

        if (ind >= (script_len - 4)/2) {
            ind = 0;
        }
    }
}

int main() {
    script_len = SCRIPT_LEN;
    script = (char *)malloc(sizeof(char) * SCRIPT_LEN);

    // header
    *(script + 0) = 0b00100100;
    *(script + 1) = 0b00100000;
    *(script + 2) = 0b00000000;
    *(script + 3) = 0b00000000; // padding

    // phrases
    *(script + 4) = 0b00111000; // phrase 1: hig | noise | custom_1 | non noise
    *(script + 5) = 0b00100011; // 2 | 3
    *(script + 6) = 0b01100101; // phrase 2: lig | non noise | med | noise
    *(script + 7) = 0b11111111; // 0 | 0

    for (int i = 0; i < 20; i ++) {
        _loop();
    }

    return 0;
}
