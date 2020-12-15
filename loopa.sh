#!/bin/bash
#SBATCH --account=project_2000028
#SBATCH -J isif7_loop
#SBATCH -o vasp_544_ifort.o%j
#SBATCH -e vasp_544_ifort.e%j
#SBATCH --partition=medium
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --time=36:00:00
##SBATCH --mem-per-cpu=4000
#SBATCH --mail-user=anna.liski@helsinki.fi
#SBATCH --mail-type=ALL

##BIN=/scratch/project_2000028/anliski/HEA/ISIFtest/ISIF2/
cp POSCAR CONTCAR
for i in 2.94 2.96 2.98 3.00 3.02 3.04 3.06 3.08 3.10 3.12 3.14 3.14496 3.15 3.16 3.18 3.20 3.22 3.24 3.26$
        rm WAVECAR
        cp CONTCAR POSCAR
        sed -i '2s/.*/'$i'/' POSCAR
        RUNNING=1
        sleep 30
        jobid=`sbatch vasp_544_mahti_ifort.sh | grep -E -o '[0-9]+(\.[0-9]+)?'`
        while [ "$RUNNING" == "1" ];
        do
          	sacct >jobinfo
                line=`grep $jobid jobinfo`
                if [[ $line == *"COMPLETED"* ]]; then
                        sleep 30
                        RUNNING=0
                else
                    	sleep 600
                fi
        sleep 30
        done
	sleep 30
        E=`tail -1 OSZICAR` ; echo $i $E  >>latticeparam_isif
sleep 30
done
cat latticeparam_isif
