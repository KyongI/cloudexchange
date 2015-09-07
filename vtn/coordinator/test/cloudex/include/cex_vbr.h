//cex_vbr.h
//
//REF : coordinator/modules/odcdriver/include/odc_vbr.hh

#ifndef _CEX_VBR_HH_
#define _CEX_VBR_HH_

#include <unc/upll_ipc_enum.h>
#include <unc/pfcdriver_ipc_enum.h>
#include <string>
#include <vector>
#include <sstream>
#include <unc_base/h> //define UncRespCode
#include "cex_common.h"
#include "cex_vtn.h"

class OdcVbrCommand {
 public:
  explicit OdcVbrCommand(ConfFileValues_t conf_values);
  ~OdcVbrCommand();

  /**
   * @brief                          - Constructs VBR command and send it to
   *                                   rest interface
   * @param[in] key_vbr              - key structure of VBR
   * @param[in] val_vbr              - value structure of VBR
   * @param[in] ctr                  - Controller pointrt
   * @return drv_resp_t              - returns UNC_RC_SUCCESS on creating vbr successfully
   *                                   /returns UNC_DRV_RC_ERR_GENERIC on failure
   */

  UncRespCode create_cmd(key_vbr_t& key_vbr,
                         val_vbr_t& val_vbr,
                         unc::driver::controller *ctr);

  /**
   * @brief                           - Constructs VBR update command and send
   *                                    it to rest interface
   * @param[in] key_vbr               - key structure of VBR
   * @param[in] val_vbr               - old value structure of VBR
   * @param[in] val_vbr               - New value structure of VBR
   * @param[in] ctr                   - Controller pointer
   * @return UncRespCode              - returns UNC_RC_SUCCESS on updating vbr successfully
   *                                    /returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode update_cmd(key_vbr_t& key_vbr,
                         val_vbr_t& val_old_vbr,
                         val_vbr_t& val_new_vbr,
                         unc::driver::controller* ctr);

  /**
   * @brief                           - Constructs VBR Delete command and send
   *                                    it to rest interface
   * @param[in] key_vbr               - key structure of VBR
   * @param[in] val_vbr               - value structure of VBR
   * @param[in] ctr                   - Controller pointer
   * @return  UncRespCode             - returns UNC_RC_SUCCESS on deleting a vbr
   *                                    / returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode delete_cmd(key_vbr_t& key_vbr,
                         val_vbr_t& val_vbr,
                         unc::driver::controller *ctr);

  /**
   * @brief                          - get vbr list - gets all the vbridge
   *                                   under particular vtn
   * @param[in]                      - vtn name
   * @param[in] ctr                  - Controller pointer
   * @param[out] cfg_node_vector     - cfg_node_vector out parameter contains
   *                                   list of vbridge present for specified vtn
   *                                   in controller
   * @return UncRespCode             - returns UNC_RC_SUCCESS on
   *                                   retrieving the vtn child successfully/
   *                                   returns UNC_DRV_RC_ERR_GENERIC on fail
   */
  UncRespCode get_vbr_list(
      std::string vtnname,
      unc::driver::controller* ctr,
      std::vector<unc::vtndrvcache::ConfigNode *> &cfg_node_vector);

};
#endif
