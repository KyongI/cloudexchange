/*
 * Copyright (c) 2014 NEC Corporation
 * All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this
 * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html
 */

package org.opendaylight.vtn.javaapi.resources.logical;

import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonObject;
import org.opendaylight.vtn.core.ipc.ClientSession;
import org.opendaylight.vtn.core.util.Logger;
import org.opendaylight.vtn.javaapi.annotation.UNCField;
import org.opendaylight.vtn.javaapi.annotation.UNCVtnService;
import org.opendaylight.vtn.javaapi.constants.VtnServiceConsts;
import org.opendaylight.vtn.javaapi.constants.VtnServiceJsonConsts;
import org.opendaylight.vtn.javaapi.exception.VtnServiceException;
import org.opendaylight.vtn.javaapi.ipc.IpcRequestProcessor;
import org.opendaylight.vtn.javaapi.ipc.enums.IpcRequestPacketEnum;
import org.opendaylight.vtn.javaapi.ipc.enums.UncCommonEnum;
import org.opendaylight.vtn.javaapi.ipc.enums.UncCommonEnum.UncResultCode;
import org.opendaylight.vtn.javaapi.ipc.enums.UncJavaAPIErrorCode;
import org.opendaylight.vtn.javaapi.ipc.enums.UncUPLLEnums;
import org.opendaylight.vtn.javaapi.resources.AbstractResource;
import org.opendaylight.vtn.javaapi.validation.logical.FlowFilterResourceValidator;

@UNCVtnService(path = "/vtns/{vtn_name}/vterminals/{vterminal_name}/interfaces/{if_name}/flowfilters")
public class VTerminalInterfaceFlowFiltersResource extends AbstractResource {
	/** The Constant LOG. */
	private static final Logger LOG = Logger.getLogger(VTerminalInterfaceFlowFiltersResource.class
			.getName());
	/**
	 * Instantiates a new VTerminalInterfaceFlowFilters Resource.
	 */
	public VTerminalInterfaceFlowFiltersResource() {
		super();
		LOG.trace("Start VTerminalInterfaceFlowFiltersResource#VTerminalInterfaceFlowFiltersResource()");
		setValidator(new FlowFilterResourceValidator(this));
		LOG.trace("Completed VTerminalInterfaceFlowFiltersResource#VTerminalInterfaceFlowFiltersResource()");
	}
	
	

	/** The vtn name. */
	@UNCField("vtn_name")
	private String vtnName;
	
	/** The vterminal name. */
	@UNCField("vterminal_name")
	private String vterminalName;
	

	/** The if name. */
	@UNCField("if_name")
	private String ifName;
	
	/**
	 * @return the vtnName
	 */
	public String getVtnName() {
		return vtnName;
	}

	/**
	 * @return the vterminalName
	 */
	public String getVterminalName() {
		return vterminalName;
	}

	/**
	 * @return the ifName
	 */
	public String getIfName() {
		return ifName;
	}



	/**
	 * Implementation of Post method of VTerminal Interface FlowFilter API
	 * 
	 * @param requestBody
	 *            the request Json object
	 * 
	 * @return Error code
	 * @throws VtnServiceException
	 */
	@Override
	public int post(final JsonObject requestBody) throws VtnServiceException {
		LOG.trace("Start VTerminalInterfaceFlowFiltersResource#post()");
		ClientSession session = null;
		IpcRequestProcessor requestProcessor = null;
		int status = ClientSession.RESP_FATAL;
		try {
			LOG.debug("Start Ipc framework call");
			session = getConnPool().getSession(
					UncUPLLEnums.UPLL_IPC_CHANNEL_NAME,
					UncUPLLEnums.UPLL_IPC_SERVICE_NAME,
					UncUPLLEnums.ServiceID.UPLL_EDIT_SVC_ID.ordinal(),
					getExceptionHandler());
			LOG.debug("Session created successfully");
			requestProcessor = new IpcRequestProcessor(session, getSessionID(),
					getConfigID(), getExceptionHandler());
			requestProcessor.createIpcRequestPacket(
					IpcRequestPacketEnum.KT_VTERM_IF_FLOWFILTER_CREATE, requestBody,
					getUriParameters(requestBody));
			LOG.debug("Request packet created successfully");
			status = requestProcessor.processIpcRequest();
			LOG.debug("Request packet processed with status" + status);
			LOG.debug("Complete Ipc framework call");
		} catch (final VtnServiceException e) {
			getExceptionHandler()
					.raise(Thread.currentThread().getStackTrace()[1]
							.getClassName()
							+ VtnServiceConsts.HYPHEN
							+ Thread.currentThread().getStackTrace()[1]
									.getMethodName(),
							UncJavaAPIErrorCode.IPC_SERVER_ERROR.getErrorCode(),
							UncJavaAPIErrorCode.IPC_SERVER_ERROR
									.getErrorMessage(), e);
			throw e;
		} finally {
			if (status == ClientSession.RESP_FATAL) {
				if (null != requestProcessor.getErrorJson()) {
					setInfo(requestProcessor.getErrorJson());
				} else {
					createErrorInfo(UncCommonEnum.UncResultCode.UNC_SERVER_ERROR
							.getValue());
				}
				status = UncResultCode.UNC_SERVER_ERROR.getValue();
			}
			getConnPool().destroySession(session);
		}
		LOG.trace("Completed VTerminalInterfaceFlowFiltersResource#post()");
		return status;
	}
	/**
	 * Add URI parameters to list
	 * 
	 * @return
	 */
	private List<String> getUriParameters(JsonObject requestBody) {
		LOG.trace("Start VRouterInterfaceFlowFilterResource#getUriParameters()");
		final List<String> uriParameters = new ArrayList<String>();
		uriParameters.add(vtnName);
		uriParameters.add(vterminalName);
		uriParameters.add(ifName);
		if (requestBody != null && requestBody.has(VtnServiceJsonConsts.INDEX)) {
			uriParameters.add(requestBody.get(VtnServiceJsonConsts.INDEX)
					.getAsString());
		}
		LOG.trace("Completed VRouterInterfaceFlowFilterResource#getUriParameters()");
		return uriParameters;
	}	
}
