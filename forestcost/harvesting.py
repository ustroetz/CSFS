import math
import operator


def harvestcost(Slope, SkidDist, RemovalsPA, VolumePA):
            
        ################################################
        # General Inputs & Functions                   #
        ################################################
        TreeVol = VolumePA/RemovalsPA

        # Buncher $/PMH
        costPMHFBDTT = 181.62   # FbuncherDriveToTree $/PMH
        costPMHFBSB = 233.61    # FbuncherSwingBoom $/PMH
        costPMHFBSL = 238.35    # FbuncherSelfLeveling $/PMH
        # Skidder $/PMH
        costPMHSS = 134.24      # Skiddersmall $/PMH
        costPMHSB = 189.93      # Skidderbig $/PMH
        ManualMachineSize = min (1.0, TreeVol/150.0)
        SkidderHourlyCost = round(costPMHSS*(1-ManualMachineSize)+costPMHSB*ManualMachineSize)
        # Processor $/PMH
        costPMHPS = 209.96      # Processorsmall $/PMH
        costPMHPB = 265.78      # Processorbig $/PMH
        MechMachineSize = min (1.0,TreeVol/80.0)
        ProcessorHourlyCost = round(costPMHPS*(1-MechMachineSize)+costPMHPB*MechMachineSize)

        WoodDensity = 58.6235

        DBH = ((TreeVol+3.675)/0.216)**0.5
        ButtDiam = DBH+3.0
        
        LogLength = 32.0
        LogsPerTree = max(1.0,(32.0/LogLength)*(-0.43+0.678*(DBH)**0.5))

        # General Functions
        def relevancefunction(cost, relevances, volumes):
            sum_map = sum(map( operator.mul, relevances, volumes))
            if sum_map == 0:
                sum_map = 0.000001
            return cost*sum(relevances)/sum_map

        def volumePMH (vol, ti):   # Volume per PMH (Volumte, Time) Function
           return (vol/(ti/60.0))


        ################################################
        # Fell and Bunch                               #
        ################################################                
        def fellbunch():                       
                # General Calculations
                if Slope<15:
                    NonSelfLevelCabDummy = 1.0
                elif Slope<35:
                    NonSelfLevelCabDummy = 1.75-0.05*Slope
                else :
                    NonSelfLevelCabDummy = 0.0

                CSlopeFB_Harv = 0.00015*Slope**2.0+0.00359*NonSelfLevelCabDummy*Slope
                CRemovalsPAFB_Harv = max(0,(0.66-0.001193*RemovalsPA*2.47+5.357*10.0**(-7.0)*(RemovalsPA*2.47)**2.0))
                costPMHFBSw=costPMHFBSB*NonSelfLevelCabDummy+costPMHFBSL*(1-NonSelfLevelCabDummy)

                DistBetweenTrees =(43560.0/(max(RemovalsPA,1)))**0.5

                # Relevance
                # Drive-to-Tree
                # Melroe Bobcat (Johnson, 79)
                if DBH<10:
                        relevanceFBDJohnson79 = 1.0
                elif DBH<15:
                        relevanceFBDJohnson79 = 3.0-DBH/5.0
                else:
                        relevanceFBDJohnson79 = 0

                if Slope<10:
                        relevanceFBDJohnson79 = relevanceFBDJohnson79
                elif Slope<20:
                        relevanceFBDJohnson79 = relevanceFBDJohnson79*(2.0-Slope/10.0)
                else:
                        relevanceFBDJohnson79 = 0

                # Chainsaw Heads (Greene&McNeel, 91)
                if DBH<15:
                        relevanceFBDGreene911 = 1.0
                elif DBH<20:
                        relevanceFBDGreene911 = 4.0-DBH/5.0
                else:
                        relevanceFBDGreene911 = 0

                if Slope<10:
                        relevanceFBDGreene911 = relevanceFBDGreene911
                elif Slope<20:
                        relevanceFBDGreene911 = relevanceFBDGreene911*(2.0-Slope/10.0)
                else:
                        relevanceFBDGreene911 = 0

                # Intermittent Circular Sawheads (Greene&McNeel, 91)
                relevanceFBDGreene912 = relevanceFBDGreene911

                # Hydro-Ax 211 (Hartsough, 01)
                if DBH<10:
                        relevanceFBDHartsough01 = 1.0
                elif DBH<15:
                        relevanceFBDHartsough01 = 3.0-DBH/5.0
                else:
                        relevanceFBDHartsough01= 0

                if Slope<10:
                        relevanceFBDHartsough01 = relevanceFBDHartsough01
                elif Slope<20:
                        relevanceFBDHartsough01 = relevanceFBDHartsough01*(2.0-Slope/10.0)
                else:
                        relevanceFBDHartsough01 = 0

                # Swing Boom
                #  Timbco 2520&Cat 227 (Johnson, 88)
                if DBH<15:
                   relevanceFBSJohnson88 = 1.0
                elif DBH<20:
                        relevanceFBSJohnson88 = 4.0-DBH/5.0
                else:
                        relevanceFBSJohnson88 = 0

                if Slope<5:
                        relevanceFBSJohnson88 = 0
                elif Slope<20:
                        relevanceFBSJohnson88 = relevanceFBSJohnson88*(-1.0/3.0+Slope/15.0)
                else:
                        relevanceFBSJohnson88 = relevanceFBSJohnson88

                # JD 693B&TJ Timbco 2518 (Gingras, 88)
                if DBH<12:
                   relevanceFBSGingras88 = 1.0
                elif DBH<18:
                        relevanceFBSGingras88 = 3.0-DBH/6.0
                else:
                        relevanceFBSGingras88 = 0

                if Slope<5:
                        relevanceFBSGingras88 = 0
                elif Slope<20:
                        relevanceFBSGingras88 = relevanceFBSGingras88*(-1.0/3.0+Slope/15.0)
                else:
                        relevanceFBSGingras88 = relevanceFBSGingras88

                # Timbco (Gonsier&Mandzak, 87)
                if DBH<15:
                   relevanceFBSGonsier87 = 1.0
                elif DBH<20:
                        relevanceFBSGonsier87 = 4.0-DBH/5.0
                else:
                        relevanceFBSGonsier87 = 0

                if Slope<15:
                        relevanceFBSGonsier87 = 0
                elif Slope<35:
                        relevanceFBSGonsier87 = relevanceFBSGonsier87*((-3.0/4.0)+(Slope/20))
                else:
                        relevanceFBSGonsier87 = relevanceFBSGonsier87

                #  FERIC Generic (Gingras, J.F., 96.  The cost of product sorting during harvesting.  FERIC Technical Note TN-245)
                if Slope<5:
                        relevanceFBSGingras96 = 0
                elif Slope<20:
                        relevanceFBSGingras96 = -1.0/3.0+Slope/15.0
                else:
                        relevanceFBSGingras96 = 1.0

                # Plamondon, J. 1998.  Trials of mechanized tree-length harvesting in eastern Canada. FERIC Technical Note TN-273)
                if TreeVol<20:
                   relevanceFBSPlamondon98 = 1.0
                elif TreeVol<50:
                        relevanceFBSPlamondon98 = 5.0/3.0-TreeVol/30.0
                else:
                        relevanceFBSPlamondon98 = 0

                if Slope<5:
                        relevanceFBSPlamondon98 = 0
                elif Slope<20:
                        relevanceFBSPlamondon98 = relevanceFBSPlamondon98*(-1.0/3.0+Slope/15.0)
                else:
                        relevanceFBSPlamondon98 = relevanceFBSPlamondon98

                # Timbco 420 (Hartsough, B., E. Drews, J. McNeel, T. Durston and B. Stokes. 97.
                if DBH<15:
                   relevanceFBSHartsough97 = 1.0
                elif DBH<20:
                        relevanceFBSHartsough97 = 4.0-DBH/5.0
                else:
                        relevanceFBSHartsough97 = 0

                if Slope<5:
                        relevanceFBSHartsough97 = 0
                elif Slope<20:
                        relevanceFBSHartsough97 = relevanceFBSHartsough97*(-1.0/3.0+Slope/15.0)
                else:
                        relevanceFBSHartsough97 = relevanceFBSHartsough97


                # Time per Tree
                TPTJohnson79 = 0.204+0.00822*DistBetweenTrees+0.02002*DBH+0.00244*Slope
                TPTGreene911 =(-0.0368+0.02914*DBH+0.00289*DistBetweenTrees+0.2134*1.1)*(1+CSlopeFB_Harv)
                TPTGreene912 =(-0.4197+0.01345*DBH+0.001245*DistBetweenTrees+0.7271*1.01)*(1+CSlopeFB_Harv)

                TPAccumHartsough01 = max(1,14.2-2.18*DBH+0.0799*DBH**2)
                TimeAccumHartsough01 = 0.114+0.266+0.073*TPAccumHartsough01+0.00999*TPAccumHartsough01*DBH
                TPPMHHartsough01 = 60*TPAccumHartsough01/TimeAccumHartsough01

                BoomReachJohnson88 = 24
                TreesInReachJohnson88 = RemovalsPA*math.pi*BoomReachJohnson88**2/43560
                TreesPCJohsnon88 = max(1,TreesInReachJohnson88)
                TPCJohnson88 = (0.242+0.1295*TreesPCJohsnon88+0.0295*DBH*TreesPCJohsnon88)*(1+CSlopeFB_Harv)
                TPTJohnson88 = TPCJohnson88/TreesPCJohsnon88

                TPTGonsier87 = (0.324+0.00138*DBH**2)*(1+CSlopeFB_Harv+CRemovalsPAFB_Harv)

                UnmerchMerchGingras88 = min(1.5,(285/(2.47*RemovalsPA)))
                TreesInReachGingras88 = RemovalsPA*math.pi*24**2/43560
                ObsTreesPerCycleGingras88 =(4.36+9-(0.12+0.34)*DBH+0.00084*2.47*RemovalsPA)/2
                TPCGingras88 = max(1,min(TreesInReachGingras88,ObsTreesPerCycleGingras88))
                TPPMHGingras88 = (127.8+21.2*TPCGingras88-63.1*UnmerchMerchGingras88+0.033*285)/(1+CSlopeFB_Harv)

                TreesInReachHartsough97 = RemovalsPA*math.pi*24**2/43560
                TreesPAccumHartsough97 = max(1,1.81-0.0664*DBH+3.64/DBH-0.0058*20.0)
                MoveFracHartsough97 = 0.5/(math.trunc(TreesInReachHartsough97/TreesPAccumHartsough97)+1)
                MoveHartsough97 = 0.192+0.00779*(24+DistBetweenTrees)
                TimeFellHartsough97 = 0.285+0.126*TreesPAccumHartsough97+0.0176*DBH*TreesPAccumHartsough97
                TPAccumHartsough97 = MoveFracHartsough97*MoveHartsough97+TimeFellHartsough97
                TPTHartsough97 = (TPAccumHartsough97*(1+0.0963)/TreesPAccumHartsough97)*(1+CSlopeFB_Harv)

                # Calculate Volume per PMH
                FBDVolumePMHJohnson79 = volumePMH (TreeVol, TPTJohnson79)
                FBDVolumePMHGreene911 = volumePMH (TreeVol, TPTGreene911)
                FBDVolumePMHGreene912 = volumePMH (TreeVol, TPTGreene912)
                FBDVolumePMHHartsough01 = TreeVol * TPPMHHartsough01
                FBSVolumePMHJohnson88 = volumePMH (TreeVol, TPTJohnson88)
                FBSVolumePMHGingras88 = TreeVol*TPPMHGingras88
                FBSVolumePMHGonsier87 = volumePMH (TreeVol, TPTGonsier87)
                FBSVolumePMHGingras96 = (50.338/0.028317*(TreeVol*0.028317)**0.3011)/(1+CSlopeFB_Harv+CRemovalsPAFB_Harv)
                FBSVolumePMHPlamondon98 =(5.0/0.028317+57.7*TreeVol)/(1.0+CSlopeFB_Harv+CRemovalsPAFB_Harv)
                FBSVolumePMHHartsough97 = volumePMH (TreeVol, TPTHartsough97)

                # Felling Cost ($/ ccf)
                CostFellBunch = round((
                        (costPMHFBDTT*relevanceFBDJohnson79
                         +costPMHFBDTT*relevanceFBDGreene911
                         +costPMHFBDTT*relevanceFBDGreene912
                         +costPMHFBDTT*relevanceFBDHartsough01
                         +costPMHFBSw*relevanceFBSJohnson88
                         +costPMHFBSw*relevanceFBSGingras88
                         +costPMHFBSL*relevanceFBSGonsier87
                         +costPMHFBSw*relevanceFBSGingras96
                         +costPMHFBSw*relevanceFBSPlamondon98
                         +costPMHFBSw*relevanceFBSHartsough97)/
                        (relevanceFBDJohnson79*FBDVolumePMHJohnson79
                         +relevanceFBDGreene911*FBDVolumePMHGreene911
                         +relevanceFBDGreene912*FBDVolumePMHGreene912
                         +relevanceFBDHartsough01*FBDVolumePMHHartsough01
                         +relevanceFBSJohnson88*FBSVolumePMHJohnson88
                         +relevanceFBSGingras88*FBSVolumePMHGingras88
                         +relevanceFBSGonsier87*FBSVolumePMHGonsier87
                         +relevanceFBSGingras96*FBSVolumePMHGingras96
                         +relevanceFBSPlamondon98*FBSVolumePMHPlamondon98
                         +relevanceFBSHartsough97*FBSVolumePMHHartsough97)), 4) 
                return CostFellBunch


        ################################################
        # Skidding                                     #
        ################################################
        def skidding():
                
                # General Calcualtions
                CSlopeSkidForwLoadSize = 1.0-0.000127*Slope**2.0
                TurnVol = 44.87*TreeVol**0.282*CSlopeSkidForwLoadSize

                # Relevance 
                # Grapple Skidders (Johnson, 88)
                if ButtDiam < 15:
                        relevanceSBJohnson88 = 1
                elif ButtDiam < 20:
                        relevanceSBJohnson88 = 4 - ButtDiam/5
                else:
                        relevanceSBJohnson88 = 0

                # Grapple Skidders (Tufts et al, 88)
                relevanceSBTufts88 = 0.5

                # John Deere 748E (Kosicki, K. 00. Productivities and costs of two harvesting trials in a western Alberta riparian zone.  FERIC Advantage 1(19))
                if TreeVol < 5:
                        relevanceSBKosicki00 = 0
                elif TreeVol < 10:
                        relevanceSBKosicki00 = -1 + TreeVol/5
                elif TreeVol < 50:
                        relevanceSBKosicki00 = 1
                elif TreeVol < 100:
                        relevanceSBKosicki00 = 2 - TreeVol/50
                else:
                        relevanceSBKosicki00 = 0

                # Cat D5H TSK Custom Track (Henderson, B. 01. Roadside harvesting with low ground-presssure skidders in northwestern British Columbia. FERIC Advantage 2(54))
                if TreeVol < 5:
                        relevanceSBHenderson01 = 0
                elif TreeVol < 10:
                        relevanceSBHenderson01 = -1 + TreeVol/5
                elif TreeVol < 50:
                        relevanceSBHenderson01 =  1
                elif TreeVol < 100:
                        relevanceSBHenderson01 = 2 - TreeVol/50
                else:
                        relevanceSBHenderson01 = 0

                # JD 748_G-II & TJ 560 (Kosicki, K. 02. Productivity and cost of summer harvesting in a central Alberta mixedwood stand. FERIC Advantage 3(6))
                if TreeVol < 30:
                        relevanceSBKosicki021 = 1
                elif TreeVol < 60:
                        relevanceSBKosicki021 = 2 - TreeVol/30
                else:
                        relevanceSBKosicki021 = 0

                # Tigercat 635 (Boswell, B. 98. Vancouver Island mechanized thinning trials. FERIC Technical Note TN-271)
                if TreeVol < 5:
                        relevanceSBBoswell98 = 0
                elif TreeVol < 10:
                        relevanceSBBoswell98 = -1 + TreeVol/5
                elif TreeVol < 100:
                        relevanceSBBoswell98 = 1
                elif TreeVol < 150:
                        relevanceSBBoswell98 = 3 - TreeVol/50
                else:
                        relevanceSBBoswell98 = 0
                        
                # Tigercat 635 (Kosicki, K. 02. Evaluation of Trans-Gesco TG88C and Tigercat 635 grapple skidders working in central Alberta. FERIC Advantage 3(37))
                if TreeVol < 40:
                        relevanceSBKosicki022 = 1
                elif TreeVol < 80:
                        relevanceSBKosicki022 = 2 - TreeVol/40
                else:
                        relevanceSBKosicki022 = 0

                relevanceSkidB = []
                relevanceSkidB.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceSB'))

                # Trees per Turn
                TreesPerTurnS = TurnVol/TreeVol
                
                # Turn relevance (lb)
                Turnrelevance = TurnVol*WoodDensity

                # Turn Time Johnson 88
                TravelEmpty = -2.179+0.0362*Slope+0.711*math.log(SkidDist)
                TravelLoaded = -0.919+0.00081*SkidDist+0.000062*Slope**3+0.353*math.log(SkidDist)
                LoadTime = max(0,0.882+0.0042*Slope**2-0.000048*(TreesPerTurnS)**3)
                DeckTime = 0.063+0.55*math.log(3)+0.0076*3*TreesPerTurnS
                turnTimeJohnson88 = TravelEmpty + TravelLoaded + LoadTime + DeckTime

                # Turn Time Tufts 88
                skidderHP=50.5+5.74*(TreeVol**0.5)
                treesPerBunch = 6 #  F44 ='Fell&Bunch'!E28 just temporary
                bunchVolume = TreeVol*treesPerBunch
                bunchesPerTurn = max(1,TurnVol/bunchVolume)
                travelEmpty =(0.1905*SkidDist+0.3557*skidderHP-0.0003336*SkidDist*skidderHP)/100
                grapple = min(5,(-38.36+161.6*bunchesPerTurn-0.5599*bunchesPerTurn*skidderHP+1.398*bunchesPerTurn*treesPerBunch)/100)
                travelLoaded =(-34.52+0.2634*SkidDist+0.7634*skidderHP-0.00122*SkidDist*skidderHP+0.03782*SkidDist*bunchesPerTurn)/100
                ungrapple = max(0,(5.177*bunchesPerTurn+0.002508*Turnrelevance-0.00007944*Turnrelevance*bunchesPerTurn*treesPerBunch*bunchesPerTurn)/100)
                turnTimeTufts88 = 1.3*(travelEmpty+grapple+travelLoaded+ungrapple)

                # Turn Time Kosicki 00
                turnTimeKosicki00 = 0.65+0.0054*SkidDist+0.244*2.1

                # Turn Time Henderson 01
                turnTimeHenderson01 = 2.818+0.0109*SkidDist

                # Turn Time Kosicki 02-1
                turnTimeKosicki021 = 0.649+0.0058*SkidDist+0.581*bunchesPerTurn

                # Turn Time Boswell 98
                turnTimeBoswell98 = 5.77 + 0.007 * SkidDist

                # Turn Time Kosicki 02-2
                turnTimeKosicki022 = 2.98+0.006*SkidDist+0.27*TreesPerTurnS

                # Skidding Volume/ PMH (ccf)
                BSkidVolPMHJohnson88 = volumePMH (TurnVol, turnTimeJohnson88)
                BSkidVolPMHTufts88 = volumePMH (TurnVol, turnTimeTufts88)
                BSkidVolPMHKosicki00 = volumePMH (TurnVol, turnTimeKosicki00)
                BSkidVolPMHHenderson01 = volumePMH (TurnVol, turnTimeHenderson01)
                BSkidVolPMHKosicki021 = volumePMH (TurnVol, turnTimeKosicki021)
                BSkidVolPMHBoswell98 = volumePMH (TurnVol, turnTimeBoswell98)
                BSkidVolPMHKosicki022 = volumePMH (TurnVol, turnTimeKosicki022)

                volumeSkidB = []
                volumeSkidB.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('BSkidVolPMH'))

                # Skidding cost ($/ ccf)
                CostSkidBun = round (relevancefunction(SkidderHourlyCost, relevanceSkidB, volumeSkidB), 4)
                
                return CostSkidBun


        ################################################
        # Process                                      #
        ################################################
        def process():
                # Relevance
                # Hahn Stroke Processor (Gonsier&Mandzak, 87)
                if DBH<15:
                        relevanceProGonsier87= 1.0
                elif DBH<20:
                        relevanceProGonsier87 = 4.0-DBH/5.0
                else:
                        relevanceProGonsier87 = 0

                #  Stroke Processor (MacDonald, 90)
                if ButtDiam<20:
                        relevanceProMacDonald90 = 1.0
                elif ButtDiam<30:
                        relevanceProMacDonald90 = 3.0-ButtDiam/10.0
                else:
                        relevanceProMacDonald90 = 0

                # Roger Stroke Processor (Johnson, 88)
                relevanceProJohnson881 = 1

                #  Harricana Stroke Processor (Johnson, 88)
                relevanceProJohnson882 = 1

                #  Hitachi EX150/Keto 500 (Schroder&Johnson, 97)
                if TreeVol<50:
                        relevanceProSchroder97 = 1
                elif TreeVol<100:
                        relevanceProSchroder97 = 2-TreeVol/50
                else:
                        relevanceProSchroder97 = 0

                # FERIC Generic (Gingras, J.F. 96)
                relevanceProGingras96 = 1

                # Valmet 546 Woodstar Processor (Holtzscher, M. and B. Lanford 1997)
                if TreeVol<20:
                        relevanceProHoltzscher97 = 1
                elif TreeVol<40:
                        relevanceProHoltzscher97 = 2-TreeVol/20
                else:
                        relevanceProHoltzscher97 = 0

                relevanceP = []
                relevanceP.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevancePro'))

                # Time per Tree
                TPTGonsier87 = 1.26*(0.232+0.0494*DBH)
                TPTMacDonald90 = 0.153+0.0145*ButtDiam
                TPTJohnson881 = -0.05+0.6844*LogsPerTree+5*10**(-8)*TreeVol**2
                TPTJohnson882 = -0.13+0.001*ButtDiam**2+0.5942*LogsPerTree
                TPTSchroder97 = (0.67+0.0116*TreeVol)**2
                TPTHoltzscher97 = -0.341+0.1243*DBH

                # Skidding Volume/ PMH (ccf)
                ProVolPMHGonsier87 = volumePMH (TreeVol, TPTGonsier87)
                ProVolPMHMacDonald90 = volumePMH (TreeVol, TPTMacDonald90)
                ProVolPMHJohnson881 = volumePMH (TreeVol, TPTJohnson881)
                ProVolPMHJohnson882 = volumePMH (TreeVol, TPTJohnson882)
                ProVolPMHSchroder97 = volumePMH (TreeVol, TPTSchroder97)
                ProVolPMHGingras96 = (41.16/0.02832)*(TreeVol/35.31)**0.4902
                ProVolPMHHoltzscher97 = volumePMH (TreeVol, TPTHoltzscher97)

                volumeP = []
                volumeP.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('ProVolPMH'))

                # Processing cost ($/ ccf)
                CostProcess = round(relevancefunction(ProcessorHourlyCost, relevanceP, volumeP),4)

                return CostProcess

             
        ################################################
        # Results                                      #
        ################################################
        CostFellBunch = fellbunch() # in $/CF
        CostSkid = skidding() # in $/CF
        CostProcess = process() # in $/CF
        Cost = (CostFellBunch + CostSkid + CostProcess) # in $/CF

        return Cost

