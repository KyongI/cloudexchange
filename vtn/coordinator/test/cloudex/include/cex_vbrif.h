//cex_vbrif.h
//
//REF : coordinator/modules/odcdriver/include/odc_vbrif.hh

#ifndef _CEX_VBRIF_HH
#define _CEX_VBRIF_HH

#include <unc/upll_ipc_enum.h>
#include <unc/pfcdriver_ipc_enum.h>
#include <string>
#include <vector>
#include <sstream>
#include <unc_base/h> //define UncRespCode
#include "cex_common.h"
#include "cex_vtn.h"

class OdcVbrIfCommand: {
 public:
  explicit OdcVbrIfCommand(unc::restjson::ConfFileValues_t conf_values);
  ~OdcVbrIfCommand();

  /**
   * @brief      - Creates VBRIf/ PortMap
   * @param[in]  - key structure of VBRIf
   * @param[in]  - value structure of VBRIf
   * @param[in]  - Controller connection information
   * @retval     - returns DRVAPI_RESPONSE SUCCESS on creation of vbrif successfully
   *               /returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode create_cmd(key_vbr_if_t& key,
                         pfcdrv_val_vbr_if_t& val,
                         unc::driver::controller *conn);

  /**
   * @brief                      - Updates VBRIf
   * @param[in] key              - key structure of VBRIf
   * @param[in] val              - Old value structure of VBRIf
   * @param[in] val              - New value structure of VBRIf
   * @param[in] conn             - Controller connection information
   * @retval UncRespCode         - returns UNC_RC_SUCCESS on updation of VBRIf
   *                               successfully/returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode update_cmd(key_vbr_if_t& key,
                         pfcdrv_val_vbr_if_t& val_old,
                         pfcdrv_val_vbr_if_t& val_new,
                         unc::driver::controller *conn);

  /**
   * @brief                    - Deletes VBRIf
   * @param[in] key            - key structure of VBRIf
   * @param[in] val            - value structure of VBRIf
   * @param[in] conn           - Controller connection information
   * @return UncRespCode       - returns UNC_RC_SUCCESS on deletion of
   *                             VBRIf successfully /returns
   *                             UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode delete_cmd(key_vbr_if_t& key,
                         pfcdrv_val_vbr_if_t& val,
                         unc::driver::controller *conn);

  /**
   * @brief                           - get all the vbr child
   * @param[in] vtn_name              - vtn name
   * @param[in] vbr_name              - vbr name
   * @param[in] ctr                   - controller pointer
   * @param[out] cfgnode_vector       - config node vector
   * @return UncRespCode              - returns UNC_RC_SUCCESS on successfully retieving a vbr
   *                                    child /returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode get_vbrif_list(
      std::string vtn_name,
      std::string vbr_name,
      unc::driver::controller* ctr,
      std::vector< unc::vtndrvcache::ConfigNode *> &cfgnode_vector);

};
#endif
