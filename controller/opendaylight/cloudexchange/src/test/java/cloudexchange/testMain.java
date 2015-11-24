package cloudexchange;

import cloudexchange.log.testLog;
import cloudexchange.service.testCEConnectionService;
import cloudexchange.service.testCEDbConfigService;
import cloudexchange.service.testCEDbInventoryListener;
import cloudexchange.service.testCEPortService;
import cloudexchange.service.testCloudExchange;
import cloudexchange.util.testUtil;

public class testMain {
	public static testCEConnectionService 		testCECS;
	public static testCEDbConfigService 		testCEDC;
	public static testCEDbInventoryListener 	testCEDI;
	public static testCEPortService 			testCEP;
	public static testCloudExchange 			testCE;
	public static testUtil 						testUtil;
	public static testLog 						testLog;

	public static void main(String[] args) {
		init();
		
		
		System.out.println(">>>>>> START TEST >>>>>>");
		runTest();
		System.out.println("<<<<<< END TEST <<<<<<");
	}
	
	
	
	
	public static void init(){
		testCECS = new testCEConnectionService();
		testCEDC = new testCEDbConfigService();
		testCEDI = new testCEDbInventoryListener();
		testCEP  = new testCEPortService();
		testCE   = new testCloudExchange();
		testUtil = new testUtil();
		testLog  = new testLog();
	}
	
	
	
	public static void runTest(){
		System.out.println(">>>>>> START TEST - testCEConnectionService >>>>>>");
		testCECS.run();
		System.out.println("<<<<<< END TEST - testCEConnectionService <<<<<<");
		
		System.out.println(">>>>>> START TEST - testCEDbConfigService >>>>>>");
		testCEDC.run();
		System.out.println("<<<<<< END TEST - testCEDbConfigService <<<<<<");
		
		System.out.println(">>>>>> START TEST - testCEDbInventoryListener >>>>>>");
		testCEDI.run();
		System.out.println("<<<<<< END TEST - testCEDbInventoryListener <<<<<<");
		
		System.out.println(">>>>>> START TEST - testCEPortService >>>>>>");
		testCEP.run();
		System.out.println("<<<<<< END TEST - testCEPortService <<<<<<");
		
		System.out.println(">>>>>> START TEST - testCloudExchange >>>>>>");
		testCE.run();  
		System.out.println("<<<<<< END TEST - testCloudExchange <<<<<<");
		
		System.out.println(">>>>>> START TEST - testUtil >>>>>>");
		testUtil.run();
		System.out.println("<<<<<< END TEST - testUtil <<<<<<");
		
		System.out.println(">>>>>> START TEST - testLog >>>>>>");
		testLog.run();
		System.out.println("<<<<<< END TEST - testLog <<<<<<");
	}
}
