package org.opendaylight.controller.cloudexchange.common;

import java.net.InetAddress;
import java.util.List;
import java.util.Map;

import org.opendaylight.controller.sal.core.Node;
import org.opendaylight.ovsdb.lib.notation.Row;

/** 
* @ClassName: Util 
* @Description: TODO Common Util
*  
*/ 
public class Util {
	/** 
	* @Title: isEmpty 
	* @Description: TODO String Empty Check
	* @param @param s 
	* @param @return
	* @return boolean
	* @throws 
	*/ 
	public static boolean isEmpty(String s){
		if(s == null || "".equals(s)) return true;
		return false;
	}
	
	/** 
	* @Title: isEmpty 
	* @Description: TODO Node Empty Check
	* @param @param n
	* @param @return
	* @return boolean
	* @throws 
	*/ 
	public static boolean isEmpty(Node n){
		if(n == null) return true;
		return false;
	}
	
	/** 
	* @Title: isEmpty 
	* @Description: TODO InetAddress Empty Check
	* @param @param ia
	* @param @return
	* @return boolean
	* @throws 
	*/ 
	public static boolean isEmpty(InetAddress ia){
		if(ia == null) return true;
		return false;
	}
	
	/** 
	* @Title: isEmpty 
	* @Description: TODO Row Empty Check
	* @param @param r
	* @param @return
	* @return boolean
	* @throws 
	*/ 
	public static boolean isEmpty(Row r){
		if(r == null) return true;
		return false;
	}
	
	/** 
	* @Title: isEmpty 
	* @Description: TODO Object Empty Check
	* @param @param o
	* @param @return
	* @return boolean
	* @throws 
	*/ 
	public static boolean isEmpty(Object o){
		if(o == null) return true;
		return false;
	}
	
	/** 
	* @Title: isEmpty 
	* @Description: TODO List Empty Check
	* @param @param l
	* @param @return
	* @return boolean
	* @throws 
	*/ 
	public static boolean isEmpty(List l){
		if(l == null || l.size() < 1) return true;
		return false;
	}
	
	/** 
	* @Title: isEmpty 
	* @Description: TODO Map Empty Check
	* @param @param m
	* @param @return
	* @return boolean
	* @throws 
	*/ 
	public static boolean isEmpty(Map m){
		if(m == null) return true;
		return false;
	}
}
