const input = document.querySelector("#mainin");
        const btn = document.querySelector("#btn");
        const output = document.querySelector("#mainout");

        let funkcje = [
            {name: /^NOP$/, code: [0, 0, 0, 0, 0]},
            {name: /^LDA$/, code: [0, 0, 0, 0, 1]},
            {name: /^ADD$/, code: [0, 0, 0, 1, 0]},
            {name: /^SUB$/, code: [0, 0, 0, 1, 1]},
            {name: /^MEMOUT$/, code: [0, 0, 1, 0, 0]},
            {name: /^MEMSAVE$/, code: [0, 0, 1, 0, 1]},
            {name: /^LDAI$/, code: [0, 0, 1, 1, 0]},
            {name: /^ADDI$/, code: [0, 0, 1, 1, 1]},
            {name: /^SUBI$/, code: [0, 1, 0, 0, 0]},
            {name: /^ALUOUT$/, code: [0, 1, 0, 0, 1]},
            {name: /^ALUCLR$/, code: [0, 1, 0, 1, 0]},
            {name: /^OPOUT$/, code: [0, 1, 0, 1, 1]},
            {name: /^JMP$/, code: [0, 1, 1, 0, 0]},
            {name: /^JSR$/, code: [0, 1, 1, 0, 1]},
            {name: /^RTS$/, code: [0, 1, 1, 1, 0]},
            {name: /^HALT$/, code: [0, 1, 1, 1, 1]},
            {name: /^LDAPTR$/, code: [1, 0, 0, 0, 0]},
            {name: /^ADDPTR$/, code: [1, 0, 0, 0, 1]},
            {name: /^SUBPTR$/, code: [1, 0, 0, 1, 0]},
            {name: /^MEMOUTPTR$/, code: [1, 0, 0, 1, 1]},
            {name: /^MEMSAVEPTR$/, code: [1, 0, 1, 0, 0]},
            {name: /^ALOOP$/, code: [1, 0, 1, 0, 1]},
            {name: /^BLOOP$/, code: [1, 0, 1, 1, 0]},
            {name: /^JMPREL$/, code: [1, 0, 1, 1, 1]},
            {name: /^JSRREL$/, code: [1, 1, 0, 0, 0]},
            {name: /^INC$/, code: [1, 1, 0, 0, 1]},
            {name: /^DEC$/, code: [1, 1, 0, 1, 0]},
            {name: /^INV$/, code: [1, 1, 0, 1, 1]},
            {name: /^SHIFT$/, code: [1, 1, 1, 0, 0]},
        ];

        let warunki = [
            {name: /^TRUE$/, code: [0, 0, 0, 0]},
            {name: /^IF=0$/, code: [0, 0, 0, 1]},
            {name: /^IF>0$/, code: [0, 0, 1, 0]},
            {name: /^IF<0$/, code: [0, 0, 1, 1]},
            {name: /^IF_OVERFLOW$/, code: [0, 1, 0, 0]},
            {name: /^FALSE$/, code: [1, 0, 0, 0]},
            {name: /^IF!=0$/, code: [1, 0, 0, 1]},
            {name: /^IF!>0$/, code: [1, 0, 1, 0]},
            {name: /^IF!<0$/, code: [1, 0, 1, 1]},
            {name: /^IF!_OVERFLOW$/, code: [1, 1, 0, 0]}
        ];

        function help(){
            console.log(funkcje);
            console.log(warunki);
        }

        function dectou2(number){
            let bitValues = [1, 2, 4, 8, 16, 32, 64, 128, -256];
            let bits = [];
            if(number > 255 || number < -256){
                console.error("Podana liczba z poza zakresu");
                return;
            }

            for(n0 = 0; n0 <= 1; n0++){
                for(n1 = 0; n1 <= 1; n1++){
                    for(n2 = 0; n2 <= 1; n2++){
                        for(n3 = 0; n3 <= 1; n3++){
                            for(n4 = 0; n4 <= 1; n4++){
                                for(n5 = 0; n5 <= 1; n5++){
                                    for(n6 = 0; n6 <= 1; n6++){
                                        for(n7 = 0; n7 <= 1; n7++){
                                            for(n8 = 0; n8 <= 1; n8++){
                                                if(number == n0 * bitValues[0] + n1 * bitValues[1] + n2 * bitValues[2] + n3 * bitValues[3] + n4 * bitValues[4] + n5 * bitValues[5] + n6 * bitValues[6] + n7 * bitValues[7] + n8 * bitValues[8]){
                                                    return [n8, n7, n6, n5, n4, n3, n2, n1, n0];
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            return bits;
        }

        btn.addEventListener("click", function(){
            let kod = input.value;
            
            //usunięcie komentarzy i pustych linijek
            kod = kod.trim().replaceAll(/(^[ \t]*\n)/gm, "").replaceAll(/\/\/.*\n/gm, "").toUpperCase();

            let jumpPoints = [];
            let kodPodzielony = kod.split("\n");
            console.log("kod podzielony");
            console.log(kodPodzielony);
            
            for(let i = 0; i < kodPodzielony.length; ++i){
                console.log("kod podzielony [i]: " + kodPodzielony[i]);
                if(kodPodzielony[i].includes(":")){
                    jumpPoints.push([kodPodzielony[i].replace(":", ""), i])
                    kodPodzielony.splice(i, 1);
                    --i;
                } else if(kodPodzielony[i].includes("=")){
                    let kodPodzielonySplit = kodPodzielony[i].split("=");
                    jumpPoints.push([kodPodzielonySplit[0].trim(), parseInt(kodPodzielonySplit[1].trim())]);
                    kodPodzielony.splice(i, 1);
                    --i;
                }
            }

            console.log(jumpPoints);
            console.log("kod podzielonyv2");
            console.log(kodPodzielony);


            let bin = [];
            let outStr = [];
            let kompilowanaLinijka, kompilowanaCzesc;
            let zawartoscKompilowanej;
            let i;

            const punkt0 = [48, 110, 1];

            output.value = "";

            let funkcja, operand, warunek;

            for(kompilowanaLinijka = 0; kompilowanaLinijka < kodPodzielony.length; kompilowanaLinijka++){
                bin[kompilowanaLinijka] = [];
                for(kompilowanaCzesc = 0; kompilowanaCzesc <= 2; kompilowanaCzesc++){
                    bin[kompilowanaLinijka][kompilowanaCzesc] = []
                    switch(kompilowanaCzesc){
                        case 0:
                            for(i = 4; i >= 0; i--){
                                bin[kompilowanaLinijka][kompilowanaCzesc][4 - i] = 0;
                            }
                            break;
                        case 1:
                            for(i = 8; i >= 0; i--){
                                bin[kompilowanaLinijka][kompilowanaCzesc][8 - i] = 0;
                            }
                            break;
                        case 2:
                            for(i = 3; i >= 0; i--){
                                bin[kompilowanaLinijka][kompilowanaCzesc][3 - i] = 0;
                            }
                            break;
                        default:
                            break;
                    }
                }
            }

            for(kompilowanaLinijka = 0; kompilowanaLinijka < kodPodzielony.length; kompilowanaLinijka++){
                zawartoscKompilowanej = kodPodzielony[kompilowanaLinijka];

                funkcja = zawartoscKompilowanej.split(' ')[0];
                operand = zawartoscKompilowanej.split(' ')[1];
                warunek = zawartoscKompilowanej.split(' ')[2];

                if(operand == undefined || operand == null){
                    operand = 0;
                }
                if(warunek == undefined || warunek == null){
                    warunek = "TRUE";
                }

                if(!(operand == undefined || operand == null) && typeof(operand) == "string"){
                    if(operand.includes("IF") || operand.includes("TRUE") || operand.includes("FALSE")){
                        warunek = operand;
                        operand = 0;
                    }
                }

                bin[kompilowanaLinijka] = [];

                for(i = 0; i < funkcje.length; i++){
                    if(funkcje[i].name.test(funkcja)){
                        bin[kompilowanaLinijka].push(funkcje[i].code);
                    }
                }

                // console.log("Tutaj!");
                // console.log("operand: " + operand);

                // console.log("Jump pointy:");
                // console.log();
                
                
                if(isNaN(operand) && !operand.includes("IF") && !operand.includes("TRUE") && !operand.includes("FALSE")){
                    try{
                        operand = jumpPoints.filter(el => {
                            return el[0] == operand;
                        })[0][1];
                    } catch {
                        console.error("Nie znaleziono odniesienia " + operand + " w linijce " + kompilowanaLinijka + ": " + zawartoscKompilowanej);
                    }
                }

                bin[kompilowanaLinijka].push(dectou2(operand));
                

                for(i = 0; i < warunki.length; i++){
                    if(warunki[i].name.test(warunek)){
                        bin[kompilowanaLinijka].push(warunki[i].code);
                        console.log("warunek: " + warunek);
                    }
                }
            }

            //console.log(bin);

            /*for(kompilowanaLinijka = 0; kompilowanaLinijka < bin.length; kompilowanaLinijka++){
                for(i = 0; i < 3; i++){
                    output.value += bin[kompilowanaLinijka][i] + "   ";
                }
                output.value += "\n";
            }*/

            for(kompilowanaLinijka = 0; kompilowanaLinijka < kodPodzielony.length; kompilowanaLinijka++){
                if(kompilowanaLinijka % 16 == 0){
                    outStr[Math.floor(kompilowanaLinijka / 16)] = "";
                    outStr[Math.floor(kompilowanaLinijka / 16)] += `summon falling_block ~ ~1 ~ {Time:1,BlockState:{Name:redstone_block},Passengers:[{id:falling_block,Passengers:[{id:falling_block,Time:1,BlockState:{Name:activator_rail},Passengers:[{id:command_block_minecart,Command:'gamerule commandBlockOutput false'},{id:command_block_minecart,Command:'data merge block ~ ~-2 ~ {auto:0}'},`;
                }
                for(kompilowanaCzesc = 0; kompilowanaCzesc <= 2; kompilowanaCzesc++){
                    switch(kompilowanaCzesc){
                        case 0:
                            for(i = 4; i >= 0; i--){
                                if(bin[kompilowanaLinijka][kompilowanaCzesc][4 - i] == 0){
                                    outStr[Math.floor(kompilowanaLinijka / 16)] += `{id:command_block_minecart,Command:'setblock ${punkt0[0] + ((Math.floor(kompilowanaLinijka % 16)) * 2)} ${punkt0[1] - (Math.floor(kompilowanaLinijka / 16) * 4)} ${(punkt0[2] + i * 2)} air'},`;
                                } else {
                                    outStr[Math.floor(kompilowanaLinijka / 16)] += `{id:command_block_minecart,Command:'setblock ${punkt0[0] + ((Math.floor(kompilowanaLinijka % 16)) * 2)} ${punkt0[1] - (Math.floor(kompilowanaLinijka / 16) * 4)} ${(punkt0[2] + i * 2)} redstone_wall_torch[facing=east]'},`;
                                }
                            }
                            break;
                        case 1:
                            for(i = 8; i >= 0; i--){
                                if(bin[kompilowanaLinijka][kompilowanaCzesc][8 - i] == 0){
                                    outStr[Math.floor(kompilowanaLinijka / 16)] += `{id:command_block_minecart,Command:'setblock ${punkt0[0] + ((Math.floor(kompilowanaLinijka % 16)) * 2)} ${punkt0[1] - (Math.floor(kompilowanaLinijka / 16) * 4)} ${(punkt0[2] + i * 2) + 10} air'},`;
                                } else {
                                    outStr[Math.floor(kompilowanaLinijka / 16)] += `{id:command_block_minecart,Command:'setblock ${punkt0[0] + ((Math.floor(kompilowanaLinijka % 16)) * 2)} ${punkt0[1] - (Math.floor(kompilowanaLinijka / 16) * 4)} ${(punkt0[2] + i * 2) + 10} redstone_wall_torch[facing=east]'},`;
                                }
                            }
                            break;
                        case 2:
                            for(i = 3; i >= 0; i--){
                                if(bin[kompilowanaLinijka][kompilowanaCzesc][3 - i] == 0){
                                    outStr[Math.floor(kompilowanaLinijka / 16)] += `{id:command_block_minecart,Command:'setblock ${punkt0[0] + ((Math.floor(kompilowanaLinijka % 16)) * 2)} ${punkt0[1] - (Math.floor(kompilowanaLinijka / 16) * 4)} ${(punkt0[2] + i * 2) + 28} air'},`;
                                } else {
                                    outStr[Math.floor(kompilowanaLinijka / 16)] += `{id:command_block_minecart,Command:'setblock ${punkt0[0] + ((Math.floor(kompilowanaLinijka % 16)) * 2)} ${punkt0[1] - (Math.floor(kompilowanaLinijka / 16) * 4)} ${(punkt0[2] + i * 2) + 28} redstone_wall_torch[facing=east]'},`;
                                }
                            }
                            break;
                        default:
                            break;
                    }
                }
                if(kompilowanaLinijka % 16 == 15 || kompilowanaLinijka == kodPodzielony.length - 1){
                    outStr[Math.floor(kompilowanaLinijka / 16)] += `{id:command_block_minecart,Command:'setblock ~ ~1 ~ command_block{auto:1,Command:"fill ~ ~ ~ ~ ~-2 ~ air"}'},{id:command_block_minecart,Command:'kill @e[type=command_block_minecart,distance=..1]'}]}]}]}`;
                }
            }

            //output.value = outStr[1];
            console.log(bin);

            output.value = "";
            for(i = 0; i <= 3; i++){
                if(outStr[i] == undefined){

                } else {
                    output.value += outStr[i] + "\n\n\n\n\n\n\n\n\n";
                }
            }
        });